# Название теста формируется по правилу:
# test_<название метода>__<проверяемый сценарий>__<ожидаемый результат>
# Тело теста состоит из трех логических блоков: arrange, act, assert

import pytest
from app.service.main import AntiplagService
from app.service.enums import Lang
from app.service.entities import (
    CheckInput,
    CheckResult,
    Candidate
)


class TestAntiplagBaseService:

    pass


class TestPycodeSimilarService:

    pass


class TestSimService:

    pass


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


