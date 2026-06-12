import pytest
from app.services.main import SimService
from app.services.entities import (
    CheckInput,
    Candidate, CheckResult,
)
from app.services.exceptions import ParsingOutputException
from app.services import messages
from app.services.enums import Lang
from app.services.utils import PlagFile


def test_get_value_from_sim_console_output__ok():

    # arrange
    check_input = 'a1.cpp consists for 62 %_ of b2.cpp material'

    check_result = 0.62

    service = SimService()

    # act
    result = service._get_value_from_sim_console_output(
        sim_console_output=check_input
    )

    # assert
    assert result == check_result


def test_get_value_from_sim_console_output__no_percent_symbol__ok():

    # arrange
    check_input = 'some console output'

    service = SimService()

    # act
    result = service._get_value_from_sim_console_output(
        sim_console_output=check_input
    )

    # assert
    assert result == 0


def test_get_value_from_sim_console_output__index_error__raise_exception():

    # arrange
    check_input = 'a1.cpp consists for 1a %_ of b2.cpp material'
    service = SimService()

    # act
    with pytest.raises(ParsingOutputException) as ex:
        service._get_value_from_sim_console_output(
            sim_console_output=check_input
        )

    # assert
    assert ex.value.message == messages.MSG_4
    assert ex.value.details == 'list index out of range'


def test_call_sim__language_cpp_identical_code__max_plagiarism():

    # arrange
    ref_code = (
        '#include <iostream>\n'
        'int main() {\n'
        '    int a, b, c;\n'
        '    std::cin >> a >> b >> c;\n'
        '    std::cout << a + b + c << \'\\n\';\n'
        '    return 0;\n'
        '}\n'
    )
    candidate_code = ref_code
    service = SimService()
    reference_file = PlagFile(code=ref_code, lang=Lang.CPP)
    candidate_file = PlagFile(code=candidate_code, lang=Lang.CPP)
    cmd = (
        f'/usr/bin/sim_c++ -r4 -s -p '
        f'{reference_file.filepath} {candidate_file.filepath}'
    )
    expected_output = (
        f'File {reference_file.filepath}: 41 tokens, 7 lines\n'
        f'File {candidate_file.filepath}: 41 tokens, 7 lines\n'
        'Total input: 2 files (2 new, 0 old), 82 tokens\n'
        '\n'
        f'{reference_file.filepath} consists for 100 % '
        f'of {candidate_file.filepath} material'
    )

    try:
        # act
        output = service._call_sim(cmd=cmd)

        # assert
        assert output == expected_output
    finally:
        candidate_file.remove()
        reference_file.remove()


def test_call_sim__language_cpp_different_code__min_plagiarism():

    # arrange
    ref_code = (
        '#include <iostream>\n'
        'int main() {\n'
        '    int a, b, c;\n'
        '    std::cin >> a >> b >> c;\n'
        '    std::cout << a + b + c << \'\\n\';\n'
        '    return 0;\n'
        '}\n'
    )
    candidate_code = (
        '#include <iostream>\n'
        '#include <vector>\n'
        '#include <algorithm>\n'
        'int main() {\n'
        '    std::vector<int> v;\n'
        '    int n, x;\n'
        '    std::cin >> n;\n'
        '    for (int i = 0; i < n; ++i) {\n'
        '        std::cin >> x;\n'
        '        v.push_back(x);\n'
        '    }\n'
        '    std::sort(v.begin(), v.end());\n'
        '    for (int val : v) std::cout << val << \' \';\n'
        '    return 0;\n'
        '}\n'
    )
    service = SimService()
    reference_file = PlagFile(code=ref_code, lang=Lang.CPP)
    candidate_file = PlagFile(code=candidate_code, lang=Lang.CPP)
    cmd = (
        f'/usr/bin/sim_c++ -r4 -s -p '
        f'{reference_file.filepath} {candidate_file.filepath}'
    )
    expected_output = (
        f'File {reference_file.filepath}: 41 tokens, 7 lines\n'
        f'File {candidate_file.filepath}: 89 tokens, 15 lines\n'
        'Total input: 2 files (2 new, 0 old), 130 tokens\n'
        '\n'
        f'{reference_file.filepath} consists for 61 % '
        f'of {candidate_file.filepath} material'
    )

    try:
        # act
        output = service._call_sim(cmd=cmd)

        # assert
        assert output == expected_output
    finally:
        candidate_file.remove()
        reference_file.remove()


def test_call_sim__language_java_identical_code__max_plagiarism():

    # arrange
    ref_code = (
        'import java.util.Scanner;\n'
        '\n'
        'public class Ref {\n'
        '    public static void main(String[] args) {\n'
        '        Scanner sc = new Scanner(System.in);\n'
        '        int a = sc.nextInt();\n'
        '        int b = sc.nextInt();\n'
        '        int c = sc.nextInt();\n'
        '        System.out.println(a + b + c);\n'
        '    }\n'
        '}\n'
    )
    candidate_code = ref_code
    service = SimService()
    reference_file = PlagFile(code=ref_code, lang=Lang.JAVA)
    candidate_file = PlagFile(code=candidate_code, lang=Lang.JAVA)
    cmd = (
        f'/usr/bin/sim_java -r4 -s -p '
        f'{reference_file.filepath} {candidate_file.filepath}'
    )
    expected_output = (
        f'File {reference_file.filepath}: 63 tokens, 11 lines\n'
        f'File {candidate_file.filepath}: 63 tokens, 11 lines\n'
        'Total input: 2 files (2 new, 0 old), 126 tokens\n'
        '\n'
        f'{reference_file.filepath} consists for 100 % '
        f'of {candidate_file.filepath} material'
    )

    try:
        # act
        output = service._call_sim(cmd=cmd)

        # assert
        assert output == expected_output
    finally:
        candidate_file.remove()
        reference_file.remove()


def test_call_sim__language_java_different_code__min_plagiarism():

    # arrange
    ref_code = (
        'import java.util.Scanner;\n'
        '\n'
        'public class Ref {\n'
        '    public static void main(String[] args) {\n'
        '        Scanner sc = new Scanner(System.in);\n'
        '        int a = sc.nextInt();\n'
        '        int b = sc.nextInt();\n'
        '        int c = sc.nextInt();\n'
        '        System.out.println(a + b + c);\n'
        '    }\n'
        '}\n'
    )
    candidate_code = (
        'public class CandDiff {\n'
        '    private int value;\n'
        '\n'
        '    public CandDiff(int value) {\n'
        '        this.value = value;\n'
        '    }\n'
        '\n'
        '    public int getValue() {\n'
        '        return value;\n'
        '    }\n'
        '}\n'
    )
    service = SimService()
    reference_file = PlagFile(code=ref_code, lang=Lang.JAVA)
    candidate_file = PlagFile(code=candidate_code, lang=Lang.JAVA)
    cmd = (
        f'/usr/bin/sim_java -r4 -s -p '
        f'{reference_file.filepath} {candidate_file.filepath}'
    )
    expected_output = (
        f'File {reference_file.filepath}: 63 tokens, 11 lines\n'
        f'File {candidate_file.filepath}: 30 tokens, 11 lines\n'
        'Total input: 2 files (2 new, 0 old), 93 tokens\n'
        '\n'
        f'{reference_file.filepath} consists for 6 % '
        f'of {candidate_file.filepath} material'
    )

    try:
        # act
        output = service._call_sim(cmd=cmd)

        # assert
        assert output == expected_output
    finally:
        candidate_file.remove()
        reference_file.remove()


def test_check_plagiarism__language_cpp_check_plagiarism__ok(mocker):

    # arrange
    lang = Lang.CPP
    ref_code = 'some reference code'
    candidate = Candidate(
        uuid='9asd2',
        code='some candidate code'
    )
    check_input = CheckInput(
        lang=lang,
        ref_code=ref_code,
        candidates=[candidate]
    )
    check_result = CheckResult(
        uuid='9asd2!2',
        percent=50.9
    )

    plag_percent_by_uuids = {'9asd2': 50.9}
    sim_cmd_output = 'some console output'

    reference_file_mock = mocker.Mock()
    reference_file_mock.filepath = '/some/reference_file.cpp'
    get_reference_file_mock = mocker.patch(
        'app.services.sim.service.SimService._get_reference_file',
        return_value=reference_file_mock
    )
    candidate_file_mock = mocker.Mock()
    candidate_file_mock.filepath = '/some/candidate_file.cpp'
    get_candidate_file_mock = mocker.patch(
        'app.services.sim.service.SimService._get_candidate_code_file',
        return_value=candidate_file_mock
    )
    call_sim_mock = mocker.patch(
        'app.services.sim.service.SimService._call_sim',
        return_value=sim_cmd_output
    )
    get_value_from_sim_console_output_mock = mocker.patch(
        'app.services.sim.service.SimService'
        '._get_value_from_sim_console_output',
        return_value=50.9
    )
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sim.service.SimService._get_candidate_with_max_plag',
        return_value=check_result
    )
    service = SimService()

    # act
    result = service.check_plagiarism(data=check_input)

    # assert
    get_reference_file_mock.assert_called_once_with(lang=lang, code=ref_code)
    get_candidate_file_mock.assert_has_calls([
        mocker.call(lang=lang, code=candidate['code'])
    ])
    call_sim_mock.assert_has_calls([
        mocker.call(
            cmd=f'/usr/bin/sim_c++ -r4 -s -p '
                f'{reference_file_mock.filepath} '
                f'{candidate_file_mock.filepath}'
        )
    ])
    get_value_from_sim_console_output_mock.assert_has_calls([
        mocker.call(sim_cmd_output)
    ])
    assert candidate_file_mock.remove.call_count == 1
    reference_file_mock.remove.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        plag_percent_by_uuids
    )
    assert result == check_result


def test_check_plagiarism__language_java_check_plagiarism__ok(mocker):

    # arrange
    lang = Lang.JAVA
    ref_code = 'some reference code'
    candidate = Candidate(
        uuid='9asd2',
        code='some candidate code'
    )
    check_input = CheckInput(
        lang=lang,
        ref_code=ref_code,
        candidates=[candidate]
    )
    check_result = CheckResult(
        uuid='9asd2!2',
        percent=50.9
    )

    plag_percent_by_uuids = {'9asd2': 50.9}
    sim_cmd_output = 'some console output'

    reference_file_mock = mocker.Mock()
    reference_file_mock.filepath = '/some/reference_file.cpp'
    get_reference_file_mock = mocker.patch(
        'app.services.sim.service.SimService._get_reference_file',
        return_value=reference_file_mock
    )
    candidate_file_mock = mocker.Mock()
    candidate_file_mock.filepath = '/some/candidate_file.cpp'
    get_candidate_file_mock = mocker.patch(
        'app.services.sim.service.SimService._get_candidate_code_file',
        return_value=candidate_file_mock
    )
    call_sim_mock = mocker.patch(
        'app.services.sim.service.SimService._call_sim',
        return_value=sim_cmd_output
    )
    get_value_from_sim_console_output_mock = mocker.patch(
        'app.services.sim.service.SimService'
        '._get_value_from_sim_console_output',
        return_value=50.9
    )
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sim.service.SimService._get_candidate_with_max_plag',
        return_value=check_result
    )
    service = SimService()

    # act
    result = service.check_plagiarism(data=check_input)

    # assert
    get_reference_file_mock.assert_called_once_with(lang=lang, code=ref_code)
    get_candidate_file_mock.assert_has_calls([
        mocker.call(lang=lang, code=candidate['code'])
    ])
    call_sim_mock.assert_has_calls([
        mocker.call(
            cmd=f'/usr/bin/sim_java -r4 -s -p '
                f'{reference_file_mock.filepath} '
                f'{candidate_file_mock.filepath}'
        )
    ])
    get_value_from_sim_console_output_mock.assert_has_calls([
        mocker.call(sim_cmd_output)
    ])
    assert candidate_file_mock.remove.call_count == 1
    reference_file_mock.remove.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        plag_percent_by_uuids
    )
    assert result == check_result
