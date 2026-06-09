from app.service.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.service.exceptions import ServiceException, UnsupportedQueryException
from app.service import messages
from app.service.enums import Lang


def test_check__ok(client, mocker):

    # arrange
    check_result = CheckResult(
        uuid='dfgh432',
        percent=50.99
    )

    check_mock = mocker.patch(
        'app.service.main.AntiplagService.check',
        return_value=check_result
    )

    # act
    response = client.post(
        '/check/',
        json={
            "lang": Lang.CPP,
            "ref_code": "some code",
            "candidates": [
                {
                    "uuid": 'abc987',
                    "code": "some code"
                },
            ]
        }
    )

    # assert
    assert response.status_code == 200
    assert 'application/json' in response.headers['content-type']
    assert response.json()['uuid'] == check_result['uuid']
    assert response.json()['percent'] == check_result['percent']
    check_mock.assert_called_once_with(
        data=CheckInput(
            lang=Lang.CPP,
            ref_code="some code",
            candidates=[
                Candidate(
                    uuid='abc987',
                    code="some code"
                )
            ]
        )
    )


def test_check__service_exception__internal_error(client, mocker):

    # arrange
    err_msg = 'some message'
    err_details = 'some details'
    mocker.patch(
        'app.service.main.AntiplagService.check',
        side_effect=ServiceException(
            message=err_msg,
            details=err_details
        )
    )

    # act
    response = client.post(
        '/check/',
        json={
            "lang": Lang.CPP,
            "ref_code": "some code",
            "candidates": [
                {
                    "uuid": 'abc987',
                    "code": "some code"
                }
            ]
        }
    )

    # assert
    assert response.status_code == 500
    assert 'application/json' in response.headers['content-type']
    assert response.json()['error'] == err_msg
    assert response.json()['details'] == err_details


def test_check__validation_error__bad_request(
    client,
    mocker
):

    # arrange
    service_mock = mocker.patch('app.service.main.AntiplagService.check')

    # act
    response = client.post(
        '/check/',
        json={
            "lang": Lang.JAVA,
            "ref_code": "some code"
        }
    )

    # assert
    assert response.status_code == 400
    assert 'application/json' in response.headers['content-type']
    assert response.json()['error'] == 'Validation Error'
    assert response.json()['details'] == {
        'candidates': [
            "Missing data for required field."
        ]
    }
    service_mock.assert_not_called()


def test_check__not_allowed_lang__bad_request(
    client,
    mocker
):

    # arrange
    service_mock = mocker.patch('app.service.main.AntiplagService.check')

    # act
    response = client.post(
        '/check/',
        json={
            "lang": "some lang",
            "ref_code": "some code",
            "candidates": [
                {
                    "uuid": 'abc987',
                    "code": "some code"
                }
            ]
        }
    )

    # assert
    assert response.status_code == 400
    assert 'application/json' in response.headers['content-type']
    assert response.json()['error'] == 'Validation Error'
    assert response.json()['details'] == {
        'lang': ['Must be one of: cpp, java, python, sql.']
    }
    service_mock.assert_not_called()


def test_check__sql_lang__ok(client, mocker):

    # arrange
    check_result = CheckResult(
        uuid='candidate-1',
        percent=0.85
    )

    check_mock = mocker.patch(
        'app.service.main.AntiplagService.check',
        return_value=check_result
    )

    # act
    response = client.post(
        '/check/',
        json={
            "lang": Lang.SQL,
            "ref_code": "SELECT id FROM users",
            "candidates": [
                {
                    "uuid": 'candidate-1',
                    "code": "SELECT id, name FROM users"
                },
            ]
        }
    )

    # assert
    assert response.status_code == 200
    assert 'application/json' in response.headers['content-type']
    assert response.json()['uuid'] == check_result['uuid']
    assert response.json()['percent'] == check_result['percent']
    check_mock.assert_called_once_with(
        data=CheckInput(
            lang=Lang.SQL,
            ref_code="SELECT id FROM users",
            candidates=[
                Candidate(
                    uuid='candidate-1',
                    code="SELECT id, name FROM users"
                )
            ]
        )
    )


def test_check__unsupported_sql_query__internal_error(client, mocker):

    # arrange
    mocker.patch(
        'app.service.main.AntiplagService.check',
        side_effect=UnsupportedQueryException()
    )

    # act
    response = client.post(
        '/check/',
        json={
            "lang": Lang.SQL,
            "ref_code": "INSERT INTO users VALUES (1)",
            "candidates": [
                {
                    "uuid": 'candidate-1',
                    "code": "INSERT INTO users VALUES (2)"
                }
            ]
        }
    )

    # assert
    assert response.status_code == 500
    assert 'application/json' in response.headers['content-type']
    assert response.json()['error'] == messages.MSG_5
    assert response.json()['details'] is None
