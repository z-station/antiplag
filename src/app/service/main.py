import pycode_similar as py_sim
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

    def _transform_plag_data(self, data) -> float:

        """ Преобразует полученный в результате
        применения Pycode_similar объект в строку,
        извлекает из нее вычисленный процент плагиата
        и возвращает его виде вещественного числа. """

        transform_to_str = str(data)
        find_plag_persent = re.findall(r'\d+\.\d+', transform_to_str)
        plag_persent = find_plag_persent.pop()
        result = float(plag_persent)
        return result

    def _check_plag_candidate(self, check_data) -> float:

        """ Осуществляет проверку на наличие плагиата
        в решении очередного кандидата для сравнения
        (на языкe программирования Python) и
        возвращает полученный процент плагиата. """

        pycheck = py_sim.detect(
            check_data,
            diff_method=py_sim.UnifiedDiff,
            keep_prints=True,
            module_level=True)
        pycheck_data = pycheck[0][1].pop(0)
        pycheck_plag_percent = self._transform_plag_data(pycheck_data)
        return pycheck_plag_percent

    def _calc_plag_results(self, plag_dict: dict) -> CheckResult:

        """ Производит подсчет результатов плагиата и возвращает
        id кандидата с максимальным процентом заимствований. """

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
        поддерживаемых детектором Pycode_similar (Python). """

        lang: str = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        lenght = len(candidate_info)
        plag_dict = {}
        for i in range(0, lenght):

            # Возвращает значения словаря candidate_info
            candidate_dict_values = candidate_info[i].values()

            # Извлекает id кандидата для сравнения
            candidate_uuid = list(candidate_dict_values)[0]

            # Извлекает код кандидата для сравнения
            candidate_code = list(candidate_dict_values)[1]

            check_data = [ref_code, candidate_code]

            result = self._check_plag_candidate(check_data)

            plag_dict.update({candidate_uuid: result})

        plag_result = self._calc_plag_results(plag_dict)
        return plag_result


class SimService(AntiplagBaseService):

    # TODO вот смотри, в докстринге ты описываешь выполняемое
    #  функцией действие, так используй те же слова и в названии функции.
    #  Судя по названию функции ты трансформируешь данные плагиата,
    #  более подходящее название функции может быть таким:
    #  _get_value_from_sim_console_output
    #  _get_plag_percent_from_console_output
    def _transform_plag_data(self, data) -> float:

        """ Извлекает вычисленный процент плагиата из данных,
        полученных в результате применения детектора SIM,
        и возвращает его в виде вещественного числа. """

        # TODO Если формат вывода sim будет отличаться то получим ValueError или TypeError
        #  например если plag_persent окажется неприводимым к int.
        #  в идеале вот тут и надо отлавливать возможную ошибку и поднимать
        #  ServiceException который на уровне фласка будет завернут в 400 ошибку
        #  и красиво показан пользователю. Сейчас рискуем получить 500.
        #  На этот кейс обязательно нужен будет unit-тест

        if '%' in data:
            find_percent = data.find('%')
            find_fragment = data[find_percent-4:find_percent]
            plag_persent = re.findall(r'\b\d+\b', find_fragment)[-1]  # опечатка в percent
            result = int(plag_persent)/100
        else:
            result = 0
        return result

    # TODO функция не считает % планиата,
    #  она возвращает кандидата с наибольшим % плагиата
    #  => глагол названия функции не совсем точно передает выполняемое действие.
    #  Например используй _get_candidate_with_max_plag
    def _calc_plag_results(self, plag_dict: dict) -> CheckResult:

        """ Возвращает кандидата с максимальным процентом заимствований. """

        # TODO объясни мне каким образом вычисляется plag_user_id
        #   я не понимаю как ты получаешь uuid пользователя с наибольшим процентом плагиата
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
            # TODO теееортически тут может случить subprocess эксцепшн если
            #   запуск команды по какой-то причине пройдет неуспешно
            #   когда будешь писать unit-тесты надо будет такой экцепшн
            #   воспроизвести, обрабатывать его и поднимать ServiceException
            #   чтобы вернуть ошибку пользователю в виде красивой 400 ошибки
            sim_cmd_output = subprocess.getoutput(
                cmd=f'{checker_command} {reference_path} {candidate_path}'
            )
            plag_percent = self._transform_plag_data(sim_cmd_output)
            candidate_uuid = candidate['uuid']
            plag_percent_by_uuids[candidate_uuid] = plag_percent
            candidate_code_file.remove()
        reference_file.remove()
        return self._calc_plag_results(plag_percent_by_uuids)


class AntiplagService:

    def check(self, data: CheckInput):

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: str = data['lang']

        if lang in Lang.SIM_LANGS:
            service = SimService()
        else:
            service = PycodeSimilarService()

        return service._check_plagiarism(data)
