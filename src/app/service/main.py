import pycode_similar as pycode
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List

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


class PycodeSimilarService(AntiplagBaseService):

    # TODO назови переменную data более содержательно и укажи ее тип
    #   например pycode_output
    def _get_value_from_pycode_output(self, data) -> float:

        """ Преобразует полученный в результате
        применения Pycode_similar объект в строку,
        извлекает из нее вычисленный процент плагиата
        и возвращает его виде вещественного числа. """

        # TODO это приведение типа тут точно нужно, какой тип приводим к str?
        transform_to_str = str(data)
        find_plag_percent = re.findall(r'\d+\.\d+', transform_to_str)
        plag_persent = find_plag_percent.pop()
        result = float(plag_persent)
        return result

    # TODO Какой тип имеет check_data, более осмысленно назвать
    #   вижу из документации pycode_similar что data это
    #   [referenced_code_str, candidate_code_str1, candidate_code_str2, ...]
    #   тогда в функцию вместо check_data более осмысленно будет передавать два аргумента:
    #   referenced_code: str и candidate_code: str, а внутри уже их пихать в метод pycode.detect
    #   * По возможности используй tuple вместо list, там где список неизменяемый т.к. list жрет оперативную память
    def _get_percent_from_pycode_candidate(self, check_data) -> float:

        """ Осуществляет проверку на наличие плагиата
        в решении очередного кандидата для сравнения
        (на языкe программирования Python) и
        возвращает полученный процент плагиата. """

        pycheck = pycode.detect(
            check_data,
            diff_method=pycode.UnifiedDiff,
            keep_prints=True,
            module_level=True)
        # TODO надо более осмысленно разобрать результат работы pycode.detect,
        #  место также содержит потенциальный AttributrError или IndexError
        #  нужна обработка случая если результат pycode.detect вернет иной результат
        #  Нужно поднимать ServiceException
        pycheck_data = pycheck[0][1].pop(0)
        pycheck_plag_percent = self._get_value_from_pycode_output(pycheck_data)
        return pycheck_plag_percent

    def _get_candidate_with_max_plag(self, plag_dict: dict) -> CheckResult:

        """ Возвращает кандидата с максимальным процентом заимствований """

        max_value_key = max(plag_dict, key=plag_dict.get)
        # TODO здесть достаточно один раз считать max, вот так
        max_value = plag_dict[max_value_key]
        uuid = None if max_value == 0 else max_value_key
        return CheckResult(
            uuid=uuid,
            percent=max_value
        )

    def _check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором Pycode_similar (Python). """

        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        plag_percent_by_uuids = {}

        for candidate in candidate_info:
            candidate_code = candidate['code']
            candidate_uuid = candidate['uuid']
            check_data = [ref_code, candidate_code]
            plag_percent = self._get_percent_from_pycode_candidate(check_data)
            plag_percent_by_uuids[candidate_uuid] = plag_percent
        return self._get_candidate_with_max_plag(plag_percent_by_uuids)


class SimService(AntiplagBaseService):

    # TODO Описать тип data, более осмысленно назвать
    def _get_value_from_sim_console_output(self, data) -> float:

        """ Извлекает вычисленный процент плагиата из данных,
        полученных в результате применения детектора SIM,
        и возвращает его в виде вещественного числа. """

        if '%' in data:
            find_percent = data.find('%')
            find_fragment = data[find_percent-4:find_percent]
            plag_percent = re.findall(r'\b\d+\b', find_fragment)[-1]
            result = int(plag_percent)/100
        else:
            result = 0
        return result

    def _get_candidate_with_max_plag(self, plag_dict: dict) -> CheckResult:

        """ Возвращает кандидата с максимальным процентом заимствований. """

        # TODO посмотри как я сделал для
        #  PycodeSimilarService._get_candidate_with_max_plag
        #  Вообще есть ощущение что эта функция одинаковая в обоих сервисах,
        #  а значит ее можно вынести в AntiplagBaseService
        plag_user_id = max(plag_dict, key=plag_dict.get)
        plag_score = max(plag_dict.values())

        uuid = None if plag_score == 0 else plag_user_id

        plag_percent = CheckResult(
            uuid=uuid,
            percent=plag_score
        )
        return plag_percent

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
