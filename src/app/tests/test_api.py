from app.service.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.service.exceptions import ServiceException
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
        path='/check/',
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
    assert response.content_type == 'application/json'
    assert response.json['uuid'] == check_result['uuid']
    assert response.json['percent'] == check_result['percent']
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
        path='/check/',
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
    assert response.content_type == 'application/json'
    assert response.json['error'] == err_msg
    assert response.json['details'] == err_details


def test_check__validation_error__bad_request(
    client,
    mocker
):

    # arrange
    service_mock = mocker.patch('app.service.main.AntiplagService.check')

    # act
    response = client.post(
        path='/check/',
        json={
            "lang": Lang.JAVA,
            "ref_code": "some code"
        }
    )

    # assert
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert response.json['error'] == 'Validation Error'
    assert response.json['details'] == {
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
        path='/check/',
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
    assert response.content_type == 'application/json'
    assert response.json['error'] == 'Validation Error'
    assert response.json['details'] == {
        'lang': ['Must be one of: cpp, java, python.']
    }
    service_mock.assert_not_called()
