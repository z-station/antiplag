import pytest
from app.services.base import AntiplagBaseService
from app.services.main import AntiplagService
from app.services.enums import Lang
from app.services.entities import (
    CheckInput,
    CheckResult,
    Candidate
)

from app.services.exceptions import (
    CandidatesException,
    LanguageException,
)
from app.services import messages


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


class TestAntiplagService:

    def test_check__language_cpp__call_sim_service__ok(self, mocker):

        # arrange
        check_input = CheckInput(
            lang=Lang.CPP,
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
            'app.services.sim.service.SimService.check_plagiarism',
            return_value=check_result
        )
        service = AntiplagService()

        # act
        result = service.check(data=check_input)

        # assert
        check_plagiarism_mock.assert_called_once_with(check_input)
        assert result == check_result

    def test_check__language_java__call_sim_service__ok(self, mocker):

        # arrange
        check_input = CheckInput(
            lang=Lang.JAVA,
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
            'app.services.sim.service.SimService.check_plagiarism',
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
            'app.services.main.PycodeSimilarService.check_plagiarism',
            return_value=check_result
        )
        service = AntiplagService()

        # act
        result = service.check(data=check_input)

        # assert
        check_plagiarism_mock.assert_called_once_with(check_input)
        assert result == check_result

    def test_check__call_sql_plag_service__ok(self, mocker):

        # arrange
        check_input = CheckInput(
            lang=Lang.SQL,
            ref_code='SELECT 1',
            candidates=[
                Candidate(
                    uuid='9asd2',
                    code='SELECT 2'
                )
            ]
        )
        check_result = CheckResult(
            uuid='9asd2',
            percent=0.7
        )
        check_plagiarism_mock = mocker.patch(
            'app.services.main.SqlPlagService.check_plagiarism',
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
