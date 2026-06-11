import pytest
import pycode_similar
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


def test_get_percent_from_pycode_candidate__return_percent__ok(mocker):

    # arrange
    reference_code = 'some code'
    candidate_code = 'some code'

    value_from_pycode_output = '55.19: ref __main__, candidate __main__'
    pycode_detect_output = [(1, [value_from_pycode_output])]

    check_result = 55.19

    service = PycodeSimilarService()

    pycode_detect_mock = mocker.patch(
        'pycode_similar.detect',
        return_value=pycode_detect_output
    )

    get_value_from_pycode_output_mock = mocker.patch(
        'app.services.pycode.service.PycodeSimilarService'
        '._get_value_from_pycode_output',
        return_value=check_result
    )

    # act
    result = service._get_percent_from_pycode_candidate(
        reference_code=reference_code,
        candidate_code=candidate_code
    )

    # assert
    pycode_detect_mock.assert_called_once_with(
        (reference_code, candidate_code),
        diff_method=pycode_similar.UnifiedDiff,
        keep_prints=True,
        module_level=True
    )
    get_value_from_pycode_output_mock.assert_called_once_with(
        value_from_pycode_output
    )
    assert result == check_result


def test_get_percent_from_pycode_candidate__pycode_error__ok(mocker):
    # arrange
    reference_code = '34f£al'
    candidate_code = 'some code'
    error_msg = 'some error'

    pycode_detect_mock = mocker.patch(
        'pycode_similar.detect',
        side_effect=SyntaxError(error_msg)
    )

    get_value_from_pycode_output_mock = mocker.patch(
        'app.services.pycode.service.PycodeSimilarService'
        '._get_value_from_pycode_output'
    )
    # act
    result = PycodeSimilarService()._get_percent_from_pycode_candidate(
        reference_code=reference_code,
        candidate_code=candidate_code
    )

    # assert
    assert result == -1
    pycode_detect_mock.assert_called_once_with(
        (reference_code, candidate_code),
        diff_method=pycode_similar.UnifiedDiff,
        keep_prints=True,
        module_level=True
    )
    get_value_from_pycode_output_mock.assert_not_called()


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
