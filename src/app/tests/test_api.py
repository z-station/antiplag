from app.service.entities import (
    Candidate,
    # TODO Сломанный импорт
    RequestPlag,
    ResponsePlag
)


class TestAPI:

    def test_check_ok(self, client, mocker):

        request_data = {
            "lang": "some lang",
            "ref_code": "some code",
            "candidates": [
                {
                    "uuid": 1,
                    "code": "another code"
                },
                {
                    "uuid": 2,
                    "code": "some code"
                },
                {
                    "uuid": 3,
                    "code": "different code"
                }
            ]
        }

        serialized_data = RequestPlag(
            lang="python",
            ref_code="some code",
            candidates=[
                    Candidate(
                        uuid=1,
                        code="another code"
                    ),
                    Candidate(
                        uuid=2,
                        code="some code"
                    ),
                    Candidate(
                        uuid=3,
                        code='different code'
                    )
            ]
        )

        testing_result = ResponsePlag(
            uuid=2,
            percent=1
        )

        testing_mock = mocker.patch(
            'app.service.main.AntiplagService.check',
            return_value=testing_result
        )

        response = client.post('/check/', json = request_data)

        assert response.status_code == 200
        assert response.json["uuid"] == testing_result.uuid
        assert response.json["percent"] == testing_result.percent
        testing_mock.assert_called_once_with(serialized_data)

    # def test_check__validation_error__bad_request(self, client, mocker):

    #     request_data = {
    #         "lang": "some lang",
    #         "ref_code": "some code",
    #         "candidates": [
    #             {
    #                 "uuid": 1,
    #                 "code": "another code"
    #             },
    #             {
    #                 "uuid": 2,
    #                 "code": "some code"
    #             },
    #             {
    #                 "uuid": 3,
    #                 "code": "different code"
    #             }
    #         ]
    #     }

    #     service_mock = mocker.patch('app.service.main.AntiplagService.check')

    #     response = client.post('/check/', json=request_data)

    #     assert response.status_code == 400