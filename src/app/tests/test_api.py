from app.service.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.service.exceptions import ServiceException


def test_check__ok(client, mocker):

    # arrange
    request_data = {
        "lang": "some lang",
        "ref_code": "some code",
        "candidates": [
            {
                "uuid": 'abc987',
                "code": "some code"
            },
        ]
    }

    serialized_data = CheckInput(
        lang="some lang",
        ref_code="some code",
        candidates=[
                Candidate(
                    uuid='abc987',
                    code="some code"
                )
        ]
    )

    check_result = CheckResult(
        uuid='dfgh432',
        percent=50.99
    )

    check_mock = mocker.patch(
        'app.service.main.AntiplagService.check',
        return_value=check_result
    )

    # act
    response = client.post('/check/', json=request_data)

    # assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json['uuid'] == check_result['uuid']
    assert response.json['percent'] == check_result['percent']
    check_mock.assert_called_once_with(
        data=serialized_data
    )


def test_check__not_uuid__zero_percent(
    client, mocker
):

    # arrange
    request_data = {
        "lang": "some lang",
        "ref_code": "some code",
        "candidates": [
            {
                "uuid": 'abc987',
                "code": "some code"
            },
        ]
    }

    serialized_data = CheckInput(
        lang="some lang",
        ref_code="some code",
        candidates=[
                Candidate(
                    uuid='abc987',
                    code="some code"
                )
        ]
    )

    check_result = CheckResult(
        uuid=None,
        percent=0
    )

    check_mock = mocker.patch(
        'app.service.main.AntiplagService.check',
        return_value=check_result
    )

    # act
    response = client.post('/check/', json=request_data)

    # assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json['uuid'] is None
    assert response.json['percent'] == 0
    check_mock.assert_called_once_with(
        data=serialized_data
    )


def test_check__service_exception__bad_request(
    client,
    mocker
):

    # arrange
    request_data = {
        "lang": "some lang",
        "ref_code": "some code",
        "candidates": [
            {
                "uuid": 'abc987',
                "code": "some code"
            },
        ]
    }

    service_ex = ServiceException(
        message='some message',
        details='some details'
    )

    mocker.patch(
        'app.service.main.AntiplagService.check',
        side_effect=service_ex
    )

    # act
    response = client.post('/check/', json=request_data)

    # assert
    assert response.status_code == 400
    assert response.content_type == 'application/json'
    assert response.json['error'] == service_ex.message
    assert response.json['details'] == service_ex.details


def test_check__validation_error__bad_request(
    client,
    mocker
):

    # arrange
    request_data = {
        "lang": "some lang",
        "ref_code": "some code"
    }

    service_mock = mocker.patch(
        'app.service.main.AntiplagService.check'
    )

    # act
    response = client.post('/check/', json=request_data)

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
