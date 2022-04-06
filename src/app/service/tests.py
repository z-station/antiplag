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

from app.service import exceptions
from app.service import messages


class TestAntiplagBaseService:

    def test_get_candidate_with_max_plag__return_candidate__nonzero(
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
            uuid='9asd2!2',
            percent=50.9
        )

        service = mocker.Mock(spec=AntiplagBaseService)
        service._get_candidate_with_max_plag.return_value = check_result

        # act
        result = service._get_candidate_with_max_plag(
            plag_dict=check_input
        )

        # assert
        assert result == check_result

    def test_get_candidate_with_max_plag__return_candidate__zero_plag(
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
            uuid=None,
            percent=0
        )

        service = mocker.Mock(spec=AntiplagBaseService)
        service._get_candidate_with_max_plag.return_value = check_result

        # act
        result = service._get_candidate_with_max_plag(
            plag_dict=check_input
        )

        # assert
        assert result == check_result    

    def test_get_candidate_with_max_plag__return_candidate__raise_exception(
        self,
        mocker
    ):

        pass

        # # arrange
        # check_input = {}

        # service = mocker.Mock(spec=AntiplagBaseService)

        # # act
        # with pytest.raises(exceptions.CandidatesException) as ex:
        #     service._get_candidate_with_max_plag(
        #         pycode_output=check_input
        #     )

        # assert ex.value.message == messages.MSG_3


class TestPycodeSimilarService:

    def test_get_value_from_pycode_output__return_value__ok(self):

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
        with pytest.raises(exceptions.CandidatesException) as ex:
            service._get_value_from_pycode_output(
                pycode_output=check_input
            )

        # assert
        assert ex.value.message == messages.MSG_3

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
            'app.service.main.PycodeSimilarService._get_value_from_pycode_output',
            return_value=check_result
        )

        # act
        result = service._get_percent_from_pycode_candidate(
            reference_code=reference_code,
            candidate_code=candidate_code
        )

        # assert
        pycode_detect_mock.assert_called_once_with(
            [reference_code, candidate_code],
            diff_method=pycode_similar.UnifiedDiff,
            keep_prints=True,
            module_level=True
        )

        get_value_from_pycode_output_mock.assert_called_once_with(
            value_from_pycode_output
        )

        assert result == check_result

    def test_get_percent_from_pycode_candidate__syntax_error__raise_exception(
        self
    ):
        # arrange
        reference_code = '34f£al'
        candidate_code = 'some code'

        # act
        with pytest.raises(exceptions.CheckerException) as ex:
            PycodeSimilarService()._get_percent_from_pycode_candidate(
                reference_code=reference_code,
                candidate_code=candidate_code
            )

        # assert
        assert ex.value.message == messages.MSG_1

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

        get_percent_from_pycode_candidate_mock = mocker.patch(
            'app.service.main.PycodeSimilarService._get_percent_from_pycode_candidate',
            return_value=50.9
        )

        get_candidate_with_max_plag_mock = mocker.patch(
            'app.service.main.AntiplagBaseService._get_candidate_with_max_plag',
            return_value=check_result
        )

        service = PycodeSimilarService()

        # act
        result = service._check_plagiarism(data=check_input)

        # assert
        get_percent_from_pycode_candidate_mock.assert_called_once_with(
            reference_code='some code',
            candidate_code='some code'
        )
        get_candidate_with_max_plag_mock.assert_called_once_with(
            {'9asd2': 50.9}
        )

        assert result == check_result


class TestSimService:

    def get_value_from_sim_console_output__return_value__ok(self):

        # arrange
        sim_console_output = 'a1.cpp consists for 62 %_ of b2.cpp material'

        check_result = 0.62

        service = AntiplagService()

        # act
        result = service._get_value_from_sim_console_output(
            sim_console_output=sim_console_output
        )

        # assert
        assert result == check_result

    def get_value_from_sim_console_output__no_percent_in_console_output__zero_result(self):

        pass

        # # arrange
        # sim_console_output = 'some result'

        # service = AntiplagService()

        # # act
        # result = service._get_value_from_sim_console_output(
        #     sim_console_output=sim_console_output
        # )

        # # assert
        # assert result == 0

    @pytest.mark.parametrize('lang', Lang.SIM_LANGS)
    def check_plagiarism__check_plagiarism__ok(
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

        sim_cmd_value = 'a1.cpp consists for 62 %_ of b2.cpp material'

        plagfile_mock = mocker.patch(
            'app.service.utils.PlagFile'
        )
        plagfile_mock.return_value.filepath.return_value = 'some path'
    
        sim_subprocces_getoutput_mock = mocker.patch(
            'subprocess.getoutput',
            return_value=sim_cmd_value
        )

        get_value_from_sim_console_output_mock = mocker.patch(
            'app.service.main.PycodeSimilarService._get_value_from_sim_console_output',
            return_value=50.9
        )

        get_candidate_with_max_plag_mock = mocker.patch(
            'app.service.main.AntiplagBaseService._get_candidate_with_max_plag',
            return_value=check_result
        )

        service = SimService()

        # act
        result = service._check_plagiarism(data=check_input)

        # assert
        sim_subprocces_getoutput_mock.assert_called_once_with(
            '/usr/bin/sim_c++ -r4 -s -p a1.cpp a2.cpp'
        )
        get_value_from_sim_console_output_mock.assert_called_once_with(
            sim_cmd_value
        )

        get_candidate_with_max_plag_mock.assert_called_once_with(
            {'9asd2': 50.9}
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
            'app.service.main.SimService._check_plagiarism',
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
            'app.service.main.PycodeSimilarService._check_plagiarism',
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
        with pytest.raises(exceptions.LanguageException) as ex:
            AntiplagService().check(data=check_input)

        # assert
        assert ex.value.message == messages.MSG_2
