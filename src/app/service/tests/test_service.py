import pytest
import pycode_similar
from app.service.main import (
    AntiplagService,
    AntiplagBaseService,
    PycodeSimilarService,
    SimService
)
from app.service.enums import Lang
from app.service.entities import (
    CheckInput,
    CheckResult,
    Candidate
)

from app.service.exceptions import (
    CandidatesException,
    LanguageException,
    ParsingOutputException
)
from app.service import messages


class TestAntiplagBaseService:

    def test_get_candidate_with_max_plag__ok(
        self,
        mocker
    ):

        # arrange
        check_input = {
            '1dfa1': 10.2,
            '53a75': 7.24,
            '9asd2': 50.9
        }
        check_result = CheckResult(
            uuid='9asd2',
            percent=50.9
        )
        mocker.patch.object(
            AntiplagBaseService,
            '__abstractmethods__',
            new_callable=set
        )
        service = AntiplagBaseService()

        # act
        result = service._get_candidate_with_max_plag(
            plag_dict=check_input
        )

        # assert
        assert result == check_result

    def test_get_candidate_with_max_plag__zero_plag__ok(
        self,
        mocker
    ):

        # arrange
        check_input = {'9asd2': 0}

        check_result = CheckResult(
            uuid=None,
            percent=0
        )
        mocker.patch.object(
            AntiplagBaseService,
            '__abstractmethods__',
            new_callable=set
        )
        service = AntiplagBaseService()

        # act
        result = service._get_candidate_with_max_plag(
            plag_dict=check_input
        )

        # assert
        assert result == check_result

    def test_get_candidate_with_max_plag__invalid_value__raise_exception(
        self,
        mocker
    ):

        # arrange
        check_input = {'9asd2': [], '123s': 12}
        mocker.patch.object(
            AntiplagBaseService,
            '__abstractmethods__',
            new_callable=set
        )
        service = AntiplagBaseService()

        # act
        with pytest.raises(CandidatesException) as ex:
            service._get_candidate_with_max_plag(check_input)

        assert ex.value.message == messages.MSG_3
        assert ex.value.details == (
            "'>' not supported between instances of 'int' and 'list'"
        )


class TestPycodeSimilarService:

    def test_get_value_from_pycode_output__ok(self):

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

    def test_get_value_from_pycode_output__index_error__raise_exception(
        self
    ):

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

    def test_get_percent_from_pycode_candidate__return_percent__ok(
        self,
        mocker
    ):

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
            'app.service.main.PycodeSimilarService'
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

    def test_get_percent_from_pycode_candidate__pycode_error__ok(
        self,
        mocker
    ):
        # arrange
        reference_code = '34f£al'
        candidate_code = 'some code'
        error_msg = 'some error'

        pycode_detect_mock = mocker.patch(
            'pycode_similar.detect',
            side_effect=SyntaxError(error_msg)
        )

        get_value_from_pycode_output_mock = mocker.patch(
            'app.service.main.PycodeSimilarService'
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

    def test_check_plagiarism__check_plagiarism__ok(
        self,
        mocker
    ):

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
            'app.service.main.PycodeSimilarService'
            '._get_percent_from_pycode_candidate',
            return_value=50.9
        )

        get_candidate_with_max_plag_mock = mocker.patch(
            'app.service.main.AntiplagBaseService'
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


class TestSimService:

    def test_get_value_from_sim_console_output__ok(self):

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

    def test_get_value_from_sim_console_output__no_percent_symbol__ok(
        self
    ):

        # arrange
        check_input = 'some console output'

        service = SimService()

        # act
        result = service._get_value_from_sim_console_output(
            sim_console_output=check_input
        )

        # assert
        assert result == 0

    def test_get_value_from_sim_console_output__index_error__raise_exception(
        self
    ):

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

    @pytest.mark.parametrize('lang', Lang.SIM_LANGS)
    def test_check_plagiarism__check_plagiarism__ok(
        self,
        lang,
        mocker
    ):
        # arrange
        check_input = CheckInput(
            lang=lang,
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

        sim_plag_dict = {'9asd2': 50.9}
        sim_cmd_output = 'some console output'

        mocker.patch('app.service.utils.PlagFile')
        mocker.patch('subprocess.getoutput', return_value=sim_cmd_output)

        get_value_from_sim_console_output_mock = mocker.patch(
            'app.service.main.SimService._get_value_from_sim_console_output',
            return_value=50.9
        )

        get_candidate_with_max_plag_mock = mocker.patch(
            'app.service.main.AntiplagBaseService._get_candidate_with_max_plag',
            return_value=check_result
        )
        service = SimService()

        # act
        result = service.check_plagiarism(data=check_input)

        # assert
        get_value_from_sim_console_output_mock.assert_called_once_with(
            sim_cmd_output
        )
        get_candidate_with_max_plag_mock.assert_called_once_with(
            sim_plag_dict
        )
        assert result == check_result


class TestAntiplagService:

    @pytest.mark.parametrize('lang', Lang.SIM_LANGS)
    def test_check__sim_langs_call_sim_service__ok(self, lang, mocker):

        # arrange
        check_input = CheckInput(
            lang=lang,
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
        check_plagiarism_mock = mocker.patch(
            'app.service.main.SimService.check_plagiarism',
            return_value=check_result
        )
        service = AntiplagService()

        # act
        result = service.check(data=check_input)

        # assert
        check_plagiarism_mock.assert_called_once_with(check_input)
        assert result == check_result

    def test_check__call_pycode_similar_service__ok(self, mocker):

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
        check_plagiarism_mock = mocker.patch(
            'app.service.main.PycodeSimilarService.check_plagiarism',
            return_value=check_result
        )
        service = AntiplagService()

        # act
        result = service.check(data=check_input)

        # assert
        check_plagiarism_mock.assert_called_once_with(check_input)
        assert result == check_result

    def test_check_invalid_language_raise_exception(self):

        # arrange
        check_input = CheckInput(
            lang='pascal',
            ref_code='some code',
            candidates=[
                Candidate(
                    uuid='9asd2',
                    code='some code'
                )
            ]
        )

        # act
        with pytest.raises(LanguageException) as ex:
            AntiplagService().check(data=check_input)

        # assert
        assert ex.value.message == messages.MSG_2
