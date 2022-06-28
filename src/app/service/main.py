import pycode_similar as pycode
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List

from app.service.enums import Lang
from app.service.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.service.utils import PlagFile
from app.service import exceptions


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
        возвращает полученный процент плагиата. """

        try:
            pycode_result = pycode.detect(
                (reference_code, candidate_code),
                diff_method=pycode.UnifiedDiff,
                keep_prints=True,
                module_level=True
            )
            pycode_output_obj = pycode_result[0][1]
            pycode_output = str(pycode_output_obj.pop())
        except (SyntaxError, IndexError) as ex:
            raise exceptions.CheckerException(details=str(ex))
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


class SimService(AntiplagBaseService):

    def _get_value_from_sim_console_output(
        self,
        sim_console_output: str
    ) -> float:

        """ Извлекает вычисленный процент плагиата из данных,
        полученных в результате применения детектора SIM,
        и возвращает его в виде вещественного числа. """

        try:
            if '%' in sim_console_output:
                percent_char_index = sim_console_output.find('%')
                value_fragment = sim_console_output[
                    percent_char_index-4: percent_char_index
                ]
                str_value = re.findall(r'\b\d+\b', value_fragment)[-1]
                result = int(str_value)/100
            else:
                result = 0
        except (IndexError, ValueError) as ex:
            raise exceptions.ParsingOutputException(details=str(ex))
        else:
            return result

    def check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором SIM (C++, Java). """

        lang: str = data['lang']
        ref_code: str = data['ref_code']
        candidates: List[Candidate] = data['candidates']

        checker_module_name = 'sim_c++' if lang == Lang.CPP else 'sim_java'
        checker_command = f'/usr/bin/{checker_module_name} -r4 -s -p'

        reference_file = PlagFile(code=ref_code, lang=lang)
        reference_path = reference_file.filepath

        plag_percent_by_uuids = {}
        for candidate in candidates:
            candidate_code_file = PlagFile(code=candidate['code'], lang=lang)
            candidate_path = candidate_code_file.filepath
            sim_cmd = subprocess.getoutput(
                cmd=f'{checker_command} {reference_path} {candidate_path}'
            )
            plag_percent = self._get_value_from_sim_console_output(sim_cmd)
            candidate_uuid = candidate['uuid']
            plag_percent_by_uuids[candidate_uuid] = plag_percent
            candidate_code_file.remove()
        reference_file.remove()
        return self._get_candidate_with_max_plag(plag_percent_by_uuids)


class AntiplagService:

    def check(self, data: CheckInput):

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: str = data['lang']

        if lang in Lang.SIM_LANGS:
            service = SimService()
        elif lang == Lang.PYTHON:
            service = PycodeSimilarService()
        else:
            raise exceptions.LanguageException()
        return service.check_plagiarism(data)

