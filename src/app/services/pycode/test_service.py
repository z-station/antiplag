import pytest
from app.services.main import PycodeSimilarService
from app.services.enums import Lang
from app.services.entities import (
    CheckInput,
    CheckResult,
    Candidate,
)
from app.services.exceptions import ParsingOutputException
from app.services import messages


def test_get_value_from_pycode_output__ok():

    # arrange
    check_input = '35.42: ref __main__<1:0>, candidate __main__<1:0>'
    check_result = 35.42
    service = PycodeSimilarService()

    # act
    result = service._get_value_from_pycode_output(
        pycode_output=check_input
    )

    # assert
    assert result == check_result


def test_get_value_from_pycode_output__index_error__raise_exception():

    # arrange
    check_input = 'ref __main__<1:0>, candidate __main__<1:0>'
    service = PycodeSimilarService()

    # act
    with pytest.raises(ParsingOutputException) as ex:
        service._get_value_from_pycode_output(
            pycode_output=check_input
        )

    # assert
    assert ex.value.message == messages.MSG_4


def test_get_percent_from_pycode__identical_code__max_plagiarism():

    # arrange
    # Идентичный код — максимальный плагиат (100%)
    reference_code = (
        'a = int(input())\n'
        'b = int(input())\n'
        'c = int(input())\n'
        'print(a + b + c)\n'
    )
    candidate_code = reference_code

    service = PycodeSimilarService()

    # act
    result = service._get_percent_from_pycode_candidate(
        reference_code=reference_code,
        candidate_code=candidate_code
    )

    # assert
    assert result == 1.0


def test_get_percent_from_pycode_candidate_different_code__min_plagiarism():

    # arrange
    # Полностью разный код — минимальный плагиат (0%)
    reference_code = (
        'a = int(input())\n'
        'b = int(input())\n'
        'c = int(input())\n'
        'print(a + b + c)\n'
    )
    candidate_code = (
        'def factorial(n):\n'
        '    result = 1\n'
        '    for i in range(2, n + 1):\n'
        '        result *= i\n'
        '    return result\n'
        'print(factorial(int(input())))\n'
    )

    service = PycodeSimilarService()

    # act
    result = service._get_percent_from_pycode_candidate(
        reference_code=reference_code,
        candidate_code=candidate_code
    )

    # assert
    assert result < 0.4


def test_get_percent_from_pycode_candidate_save_code__partial_plagiarism():

    # arrange
    # Та же задача (сумма трёх чисел), но реализована через цикл — частичный плагиат
    reference_code = (
        'a = int(input())\n'
        'b = int(input())\n'
        'c = int(input())\n'
        'print(a + b + c)\n'
    )
    candidate_code = (
        'numbers = []\n'
        'for _ in range(3):\n'
        '    numbers.append(int(input()))\n'
        'print(sum(numbers))\n'
    )

    service = PycodeSimilarService()

    # act
    result = service._get_percent_from_pycode_candidate(
        reference_code=reference_code,
        candidate_code=candidate_code
    )

    # assert
    assert result < 0.2


def test_check_plagiarism__check_plagiarism__ok(mocker):

    # arrange
    check_input = CheckInput(
        lang=Lang.PYTHON,
        ref_code='some code',
        candidates=[
            Candidate(
                uuid='9asd2',
                code='some code'
            )
        ]
    )
    check_result = CheckResult(
        uuid='9asd2!2',
        percent=50.9
    )

    pycode_plag_dict = {'9asd2': 50.9}

    get_percent_from_pycode_candidate_mock = mocker.patch(
        'app.services.pycode.service.PycodeSimilarService'
        '._get_percent_from_pycode_candidate',
        return_value=50.9
    )

    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.base.AntiplagBaseService'
        '._get_candidate_with_max_plag',
        return_value=check_result
    )
    service = PycodeSimilarService()

    # act
    result = service.check_plagiarism(data=check_input)

    # assert
    get_percent_from_pycode_candidate_mock.assert_called_once_with(
        reference_code='some code',
        candidate_code='some code'
    )
    get_candidate_with_max_plag_mock.assert_called_once_with(
        pycode_plag_dict
    )

    assert result == check_result
