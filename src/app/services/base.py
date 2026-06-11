from abc import ABC, abstractmethod

from app.services.entities import (
    CheckInput,
    CheckResult
)
from app.services import exceptions


class AntiplagBaseService(ABC):

    @abstractmethod
    def check_plagiarism(self, data: CheckInput) -> CheckResult:
        pass

    def _get_candidate_with_max_plag(self, plag_dict: dict) -> CheckResult:

        """ Возвращает кандидата с максимальным процентом заимствований. """

        try:
            max_value_key = max(plag_dict, key=plag_dict.get)
            max_value = plag_dict[max_value_key]
            uuid = None if max_value == 0 else max_value_key
        except (ValueError, TypeError) as ex:
            raise exceptions.CandidatesException(details=str(ex))
        else:
            return CheckResult(
                uuid=uuid,
                percent=max_value
            )
