import pycode_similar
import subprocess
import re
from abc import ABC, abstractmethod
from typing import List

from enums import Lang
from entities import Candidates, RequestPlag, ResponsePlag


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
            и возвращает его виде целого числа. """

        to_str = str(data)
        out = (re.findall("\d+\.\d+", to_str)).pop()
        if len(out) <= 3:
            if out[0] == "1":
                result = 100
            else:
                elem = out[2:]
                result = int(elem) * 10
        else:
            result = int(out[2:])
        return result
    
    def _check(self, data: RequestPlag) -> ResponsePlag:
        
        """ Проверка на плагиат исходного кода задач на языках, 
            поддерживаемых детектором Pycode_similar (Python). """

        lang: Lang.CHOICES = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        if lang == Lang.PYTHON:
            lenght = len(candidate_info)
            plag_dict = {}
            for i in range(0, lenght):
                candidate_code = list(candidate_info[i].values())[1]
                pycheck = pycode_similar.detect([ref_code, candidate_code], 
                                          diff_method=pycode_similar.UnifiedDiff, 
                                          keep_prints=True, module_level=True)
                result = self._transform(pycheck[0][1].pop(0))
                plag_dict.update({list(candidate_info[i].values())[0]: result})
            plag_user_id = max(plag_dict, key=plag_dict.get)
            plag_score = max(plag_dict.values())
            plagiarism = ResponsePlag(
                uuid = plag_user_id, 
                result = plag_score
            )
            return plagiarism    


class SimService(AntiplagBaseService):

    def _transform(self, data) -> int:
        
        """ Извлекает вычисленный процент плагиата из данных, 
            полученных в результате применения детектора SIM, 
            и возвращает его в виде целого числа. """

        out = (re.findall(r'\b\d+\b', data))[-1]
        result = int(out)
        return result

    def _check(self, data: RequestPlag) -> ResponsePlag:

        """ Проверка на плагиат исходного кода задач на языках, 
            поддерживаемых детектором SIM (C++, Java). """

        lang: Lang.CHOICES = data['lang']
        ref_code: str = data['ref_code']
        candidate_info: List[Candidates] = data['candidate_info']

        lenght = len(candidate_info)
        plag_dict = {}
        
        if lang == Lang.CPP:
            # TODO
            #  1. Нужно определить какую-то конкретную директорию на диске
            #  где будут создаваться эти временные файлы
            #  2. Названия файлов должны быть уникальными, т.к. если
            #  параллельно будет работать нескольк инстансов сервиса то они
            #  будут читать и писать в одни и те же файлы
            #  3. После оконкчания работы нужно удалять файлы
            #  4. В идеале каждая функция должна делать одну вещь потому
            #  управление файлами нужно вынести в отдельную утилиту
            #  Смотри пример реализации тут https://github.com/z-station/sandbox-python38/blob/master/src/app/entities/translator.py
            #  Управление файлами сделано через класс PythonFile,
            #  здесь нужно сделать нечто похожее

            file_1, file_2 = 't1.cpp', 't2.cpp'
            settings = 'sim_c++ -r4 -s -p  t1.cpp t2.cpp'
        elif lang == Lang.JAVA:
            file_1, file_2 = 't1.java', 't2.java'
            settings = 'sim_java -r4 -s -p  t1.java t2.java'
        
        ref = open(file_1, "w+")
        ref.write(ref_code)
        ref.close()
        for i in range(0, lenght):
            candidate_code = list(candidate_info[i].values())[1]
            with open(file_2, "w+") as cand:
                cand.write(candidate_code)
                cand.close()
            simcheck = subprocess.getoutput(settings)
            result = self._transform(simcheck)
            plag_dict.update({list(candidate_info[i].values())[0]: result})
        plag_user_id = max(plag_dict, key=plag_dict.get)
        plag_score = max(plag_dict.values())
        plagiarism = ResponsePlag(
            uuid = plag_user_id,
            result = plag_score
        )
        return plagiarism


class AntiplagService:

    def perform(self, data: RequestPlag ) -> None:
        # TODO давай назовем этот метод check

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: Lang.CHOICES = data['lang']

        if lang == Lang.PYTHON:
            obj = PycodeSimilarService()
        elif lang == Lang.CPP or lang == Lang.JAVA:
            obj = SimService()
        return obj._check(data)
