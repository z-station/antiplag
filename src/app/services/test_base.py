import pytest
from app.services.base import AntiplagBaseService
from app.services.entities import CheckResult
from app.services.exceptions import CandidatesException


class _ConcreteService(AntiplagBaseService):
    """Минимальная реализация абстрактного класса для тестирования."""

    def check_plagiarism(self, data):
        pass


def test_get_candidate_with_max_plag__single_candidate__ok():

    # arrange
    service = _ConcreteService()
    plag_dict = {'candidate-1': 0.75}

    # act
    result = service._get_candidate_with_max_plag(plag_dict)

    # assert
    assert result == CheckResult(uuid='candidate-1', percent=0.75)


def test_get_candidate_with_max_plag__multiple__returns_max():

    # arrange
    service = _ConcreteService()
    plag_dict = {
        'candidate-1': 0.3,
        'candidate-2': 0.9,
        'candidate-3': 0.6,
    }

    # act
    result = service._get_candidate_with_max_plag(plag_dict)

    # assert
    assert result == CheckResult(uuid='candidate-2', percent=0.9)


def test_get_candidate_with_max_plag__all_zero__uuid_is_none():

    # arrange
    service = _ConcreteService()
    plag_dict = {
        'candidate-1': 0.0,
        'candidate-2': 0.0,
    }

    # act
    result = service._get_candidate_with_max_plag(plag_dict)

    # assert
    assert CheckResult(uuid=None, percent=0)


def test_get_candidate_with_max_plag__empty_dict__raise_exception():

    # arrange
    service = _ConcreteService()

    # act
    with pytest.raises(CandidatesException) as ex:
        service._get_candidate_with_max_plag({})

    # assert
    assert ex.value.message is not None
