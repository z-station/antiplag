import pycode_similar as py_sim
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List

from app.service.enums import Lang
from app.service.entities import (
    Candidates,
    RequestPlag,
    ResponsePlag
)
from app.service.utils import PlagFile


class AntiplagBaseService(ABC):

    @abstractmethod
    def _transform(self, data) -> int:
        pass

    @abstractmethod
    def _check(self, data: RequestPlag) -> ResponsePlag:
        pass


class PycodeSimilarService(AntiplagBaseService):

    def _transform(self, data) -> int:

        """ Преобразует полученный в результате
        применения Pycode_similar объект в строку,
        извлекает из нее вычисленный процент плагиата
        и возвращает его виде вещественного числа. """

        to_str = str(data)
        out = (re.findall(r'\d+\.\d+', to_str)).pop()
        result = float(out)
        return result

    def _check(self, data: RequestPlag) -> ResponsePlag:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором Pycode_similar (Python). """

        lang: str = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        if lang == Lang.PYTHON:
            lenght = len(candidate_info)
            plag_dict = {}
            for i in range(0, lenght):
                candidate_code = list(candidate_info[i].values())[1]
                pycheck = py_sim.detect(
                    [ref_code, candidate_code],
                    diff_method=py_sim.UnifiedDiff,
                    keep_prints=True,
                    module_level=True)
                result = self._transform(pycheck[0][1].pop(0))
                plag_dict.update({list(candidate_info[i].values())[0]: result})
            plag_user_id = max(plag_dict, key=plag_dict.get)
            plag_score = max(plag_dict.values())
            if plag_score == 0:
                plagiarism = ResponsePlag(
                    uuid=None,
                    percent=0
                )
            else:
                plagiarism = ResponsePlag(
                    uuid=plag_user_id,
                    percent=plag_score
                )
            return plagiarism


class SimService(AntiplagBaseService):

    # TODO названим функции должен быть глагол который
    #  описывает выполняемое действие, напимер get_plagiarism_percent
    def _transform(self, data) -> int:

        """ Извлекает вычисленный процент плагиата из данных,
        полученных в результате применения детектора SIM,
        и возвращает его в виде вещественного числа. """

        if '%' in data:
            percent = data.find('%')
            fragment = data[percent-4:percent]
            out = re.findall(r'\b\d+\b', fragment)[-1]
            result = int(out)/100
        else:
            result = 0
        return result

    def _check(self, data: RequestPlag) -> ResponsePlag:

        """ Проверка на плагиат исходного кода задач на языках,
        поддерживаемых детектором SIM (C++, Java). """

        lang: str = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        lenght = len(candidate_info) # TODO опечатка: length
        plag_dict = {}

        # TODO можно написать элегантнее без дублирования
        # checker_module_name = 'sim_c++' if lang == Lang.CPP else 'sim_java'
        # checker_command = f'/usr/bin/{checker_module_name} -r4 -s -p'
        if lang == Lang.CPP:
            settings = '/usr/bin/sim_c++ -r4 -s -p'
        elif lang == Lang.JAVA:
            settings = '/usr/bin/sim_java -r4 -s -p'


        # TODO что значит ref ??? Нейминг!!!!
        ref = PlagFile(code=ref_code, lang=lang)

        # TODO итерируй по элементам
        for i in range(0, lenght):
            # TODO Рекомендую вынести в отдельную функцию проверку очередного кандидата
            #  на плагиат - юнит тесты будет писать проще

            # TODO Рекомендую вынести получение консольной команды sim в отдельную функцию

            # TODO непонятный код, здесь у тебя подразумевается обращение
            #  к какой-то чежстко фиксированной структуре, но из кода не понятно,
            #  это просто куча операторов в одной строке которые что-то делают,
            #  опиши более детально, разбей на несколько строк "Сложное лучше чем запутанное, а простое лучше сложного"
            candidate_code = list(candidate_info[i].values())[1]
            # TODO нейминг переменных!! что за cand, как это связано с содержимым? candidate_code_file больше отражает содердимое
            cand = PlagFile(code=candidate_code, lang=lang)

            # TODO Можно сделать более читаемо:
            # cmd = f'{command} {path_1} {path_2}'.format(
            #    command=checker_command,
            #    path_1=code_file.filepath,
            #    path_2=candidate_code_file.filepath
            # )
            sim_tuple = (settings, ref.filepath, cand.filepath)
            sim_settings = ' '.join(sim_tuple)
            # TODO что за simcheck, как я из названия должен
            #  понять что содержится внутри переменной? Нейминг!!!!

            simcheck = subprocess.getoutput(sim_settings)
            result = self._transform(simcheck)
            # TODO такие конструкции это не pythonic стиль программирования,
            #  код должен быть простым, читаемым. Убрать много вложенностей
            #  и разложить на читаемые конструкции
            plag_dict.update({list(candidate_info[i].values())[0]: result})
            cand.remove()
        ref.remove()
        # TODO подсчет плагиата лучше вынести в отдельную функцию
        plag_user_id = max(plag_dict, key=plag_dict.get)
        plag_score = max(plag_dict.values())
        # TODO Дублирование кода можно убрать
        if plag_score == 0:
            plagiarism = ResponsePlag(
                uuid=None, # TODO аннотирование атрибута в ResponsePlag не допускает значение None
                percent=0
            )
        else:
            plagiarism = ResponsePlag(
                uuid=plag_user_id,
                percent=plag_score
            )
        return plagiarism


class AntiplagService:

    # TODO Если функция ничего не возвращает то не нужно писать аннотирование  -> None:
    # TODO в твоем случае функция вообще то возвращает кое что
    def check(self, data: RequestPlag) -> None:

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: str = data['lang']

        if lang == Lang.PYTHON:
            obj = PycodeSimilarService()
        # TODO удачнее будет все языки поделить по группам относительно sim или
        #  PycodeSImilar и проверять к какой группе принадлежит язык типа: if lang in Lang.SIM_LANGS
        elif lang == Lang.CPP or lang == Lang.JAVA:
            obj = SimService()
        return obj._check(data)
