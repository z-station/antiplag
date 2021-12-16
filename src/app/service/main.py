import pycode_similar as py_sim
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List

from app.service.enums import Lang
from app.service.entities import (
    Candidates,
    RequestPlag,
    ResponsePlag)
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

        lenght = len(candidate_info)
        plag_dict = {}

        if lang == Lang.CPP:
            settings = '/usr/bin/sim_c++ -r4 -s -p'
        elif lang == Lang.JAVA:
            settings = '/usr/bin/sim_java -r4 -s -p'

        ref = PlagFile(code=ref_code, lang=lang)

        for i in range(0, lenght):
            candidate_code = list(candidate_info[i].values())[1]
            cand = PlagFile(code=candidate_code, lang=lang)
            sim_tuple = (settings, ref.filepath, cand.filepath)
            sim_settings = ' '.join(sim_tuple)
            simcheck = subprocess.getoutput(sim_settings)
            result = self._transform(simcheck)
            plag_dict.update({list(candidate_info[i].values())[0]: result})
            cand.remove()
        ref.remove()
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


class AntiplagService:

    def check(self, data: RequestPlag) -> None:

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: str = data['lang']

        if lang == Lang.PYTHON:
            obj = PycodeSimilarService()
        elif lang == Lang.CPP or lang == Lang.JAVA:
            obj = SimService()
        return obj._check(data)
