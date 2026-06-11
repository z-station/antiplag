import pytest
from app.services.main import SimService
from app.services.entities import (
    CheckInput,
    Candidate,
)
from app.services.exceptions import ParsingOutputException
from app.services import messages
from app.services.enums import Lang


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


def test_check_plagiarism__language_java_check_plagiarism__ok():

    # arrange
    check_input = CheckInput(
        lang=Lang.JAVA,
        ref_code='some code 1',
        candidates=[
            Candidate(
                uuid='9asd2',
                code='some code 1'
            )
        ]
    )

    service = SimService()

    # act
    result = service.check_plagiarism(data=check_input)

    # assert
    assert result == {'percent': 50.9, 'uuid': '9asd2doc'}


def test_check_plagiarism__language_cpp_check_plagiarism__ok():

    # arrange
    check_input = CheckInput(
        lang=Lang.JAVA,
        ref_code='some code 1',
        candidates=[
            Candidate(
                uuid='9asd2',
                code='some code 1'
            )
        ]
    )

    service = SimService()

    # act
    result = service.check_plagiarism(data=check_input)

    # assert
    assert result == {'percent': 50.9, 'uuid': '9asd2doc'}
