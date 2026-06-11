import pycode_similar as pycode
import re
from typing import List

from app.services.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.services import exceptions
from app.services.base import AntiplagBaseService


class PycodeSimilarService(AntiplagBaseService):

    def _get_value_from_pycode_output(self, pycode_output: str) -> float:

        """ Ивлекает из строки вычисленный процент плагиата
        и возвращает его виде вещественного числа. """

        try:
            pycode_output_str = str(pycode_output)
            values = re.findall(r'\d+\.\d+', pycode_output_str)
            return float(values.pop())
        except IndexError as ex:
            raise exceptions.ParsingOutputException(details=str(ex))

    def _get_percent_from_pycode_candidate(
        self,
        reference_code: str,
        candidate_code: str
    ) -> float:

        """ Осуществляет проверку на наличие плагиата
        в решении очередного кандидата для сравнения
        (на языкe программирования Python) и
        возвращает полученный процент плагиата.

        Возвращает -1 если бекенд плагиата возвращает ошибку при очередного
        кандидата. Это означает что проверить плагиат невозможно.
        """

        try:
            pycode_result = pycode.detect(
                (reference_code, candidate_code),
                diff_method=pycode.UnifiedDiff,
                keep_prints=True,
                module_level=True
            )
            pycode_output_obj = pycode_result[0][1]
            pycode_output = str(pycode_output_obj.pop())
        except (SyntaxError, IndexError):
            return -1
        else:
            pycheck_plag_percent = self._get_value_from_pycode_output(
                pycode_output
            )
            return pycheck_plag_percent

    def check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором Pycode_similar (Python). """

        ref_code: str = data['ref_code']
        candidates: List[Candidate] = data['candidates']

        plag_percent_by_uuids = {}

        for candidate in candidates:
            candidate_code = candidate['code']
            candidate_uuid = candidate['uuid']
            plag_percent = self._get_percent_from_pycode_candidate(
                reference_code=ref_code,
                candidate_code=candidate_code
            )
            plag_percent_by_uuids[candidate_uuid] = plag_percent
        return self._get_candidate_with_max_plag(plag_percent_by_uuids)
