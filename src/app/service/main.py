import pycode_similar as pycode
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List
from pycode_similar import FuncDiffInfo

from app.service.enums import Lang
from app.service.entities import (
    Candidates,
    CheckInput,
    CheckResult
)
from app.service.utils import PlagFile


class AntiplagBaseService(ABC):

    @abstractmethod
    def _check_plagiarism(self, data: CheckInput) -> CheckResult:
        pass

    def _get_candidate_with_max_plag(self, plag_dict: dict) -> CheckResult:

        """ Возвращает кандидата с максимальным процентом заимствований. """

        max_value_key = max(plag_dict, key=plag_dict.get)
        max_value = plag_dict[max_value_key]
        uuid = None if max_value == 0 else max_value_key
        return CheckResult(
            uuid=uuid,
            percent=max_value
        )


class PycodeSimilarService(AntiplagBaseService):

    def _get_value_from_pycode_output(
        self,
        pycode_output: FuncDiffInfo
    ) -> float:

        """ Преобразует полученный в результате
        применения Pycode_similar объект в строку,
        извлекает из нее вычисленный процент плагиата
        и возвращает его виде вещественного числа. """

        pycode_output_str = str(pycode_output)
        values = re.findall(r'\d+\.\d+', pycode_output_str)
        return float(values.pop())

    def _get_percent_from_pycode_candidate(
        self,
        referenced_code: str,
        candidate_code: str
    ) -> float:

        """ Осуществляет проверку на наличие плагиата
        в решении очередного кандидата для сравнения
        (на языкe программирования Python) и
        возвращает полученный процент плагиата. """

        pycheck = pycode.detect(
            [referenced_code, candidate_code],
            diff_method=pycode.UnifiedDiff,
            keep_prints=True,
            module_level=True)
        pycheck_data = pycheck[0][1].pop(0)
        pycheck_plag_percent = self._get_value_from_pycode_output(pycheck_data)
        return pycheck_plag_percent

    def _check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором Pycode_similar (Python). """

        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        plag_percent_by_uuids = {}

        for candidate in candidate_info:
            candidate_code = candidate['code']
            candidate_uuid = candidate['uuid']
            # TODO Когда в функция принимает больше одного аргумента
            #  - используй именованные аргументы. Это нужно для гибкости кода.
            #  Если автор функции добавит новые аргументы
            #  или изменит порядок существующих - твой код не сломается, только
            #  если аргументы именованные.
            plag_percent = self._get_percent_from_pycode_candidate(
                ref_code,
                candidate_code) # TODO Закрывающая скобка всегда на новой строке
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

        if '%' in sim_console_output:
            percent_char_index = sim_console_output.find('%')
            value_fragment = sim_console_output[
                percent_char_index-4: percent_char_index
            ]
            str_value = re.findall(r'\b\d+\b', value_fragment)[-1]
            result = int(str_value)/100
        else:
            result = 0
        return result

    def _check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором SIM (C++, Java). """

        lang: str = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        checker_module_name = 'sim_c++' if lang == Lang.CPP else 'sim_java'
        checker_command = f'/usr/bin/{checker_module_name} -r4 -s -p'

        reference_file = PlagFile(code=ref_code, lang=lang)
        reference_path = reference_file.filepath

        plag_percent_by_uuids = {}
        for candidate in candidate_info:
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
        else:
            service = PycodeSimilarService()

        return service._check_plagiarism(data)
