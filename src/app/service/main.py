import pycode_similar
import subprocess
import re
import sys

# TODO Давай зафиксируем версию питона на которой работает наш проект
#  это или 3.7 или 3.8. Это зафиксировать:
#  - в ТЗ
#  - в Pipfile проекта
#  - в данном участке кода выбрать 1 вариант
if sys.version_info >= (3, 8):
    from typing import TypedDict, List
else:
    from typing_extensions import TypedDict
    from typing import List

# TODO Создай файл service/entities.py и вынеси туда классы сущностей:
#  - Candidate
#  - PlagResult
class Candidate(TypedDict):

    uuid: str
    code: str


class PlagResult(TypedDict):

    uuid: str
    result: int


# TODO Создай файл service/enums.py и вынеси туда классы перечислений:
#  - Lang
class Lang:

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (PYTHON, PYTHON)
    )

# TODO Сам сервис мы разделим на 4 части которые отвечают
#  за разные уровни абстракции, позволят инкапсулировать логику,
#  добавить гибкость при масштабировании и написании unit-тестов:
#  1. class AntiplagBaseService - реализует интерфейсы публичных методов
#  сервиса + методы общие и для pycode_similar и для sim
#  2. class PycodeSimilarService(AntiplagBaseService) - реализует
#  публичные методы AntiplagBaseService и реализует проверку антиплагиата
#  через pycode_similar
#  3. class SimService(AntiplagBaseService) - реализует
#  публичные методы AntiplagBaseService и реализует проверку антиплагиата
#  через sim
#  4. class AntiplagService - высокоуровневый сервис, принимает запрос,
#  и в зависимости от ЯП передает его на обработку на нижележащий уровень либо
#  в PycodeSimilarService либо в SimService, возвращает результат обработки
#  с нижележащего уровня, сам никаких вычислений не производит.


class CappaPlag:

    def _py_transform(self, data) -> int:

        """ Преобразует полученный в результате
        применения Pycode_similar объект в строку, 
        извлекает из нее вычисленный процент плагиата 
        и возвращает его виде целого числа """

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
    
    def _sim_transform(self, data) -> int:

        """ Извлекает вычисленный процент плагиата из данных, 
        полученных в результате применения детектора SIM, 
        и возвращает его в виде целого числа """

        out = (re.findall(r'\b\d+\b', data))[-1]
        result = int(out)
        return result
    
    def _sim_check(
        self, 
        sim_settings: str, 
        sim_lang: Lang.CHOICES,
        ref_code: str, 
        candidate_info: List[Candidate]
    ) -> PlagResult:
        
        """ Проверка на плагиат исходного кода задач на языках, 
        поддерживаемых детектором SIM (C++, Java) """

        lenght = len(candidate_info)
        plag_dict = {}
        
        if sim_lang == Lang.CPP:
            file_1, file_2 = 't1.cpp', 't2.cpp'
        elif sim_lang == Lang.JAVA:
            file_1, file_2 = 't1.java', 't2.java'
        
        ref = open(file_1, "w+")
        ref.write(ref_code)
        ref.close()
        for i in range(0, lenght):
            candidate_code = list(candidate_info[i].values())[1]
            with open(file_2, "w+") as cand:
                cand.write(candidate_code)
                cand.close()
            simcheck = subprocess.getoutput(sim_settings)
            result = self._sim_transform(simcheck)
            plag_dict.update({list(candidate_info[i].values())[0]: result})
        plag_user_id = max(plag_dict, key=plag_dict.get)
        plag_score = max(plag_dict.values())
        plagiarism = PlagResult(
            uuid = plag_user_id,
            result = plag_score
        )
        return plagiarism
    
    def check(
        self, 
        lang: Lang.CHOICES, 
        ref_code: str, 
        candidate_info: List[Candidate]
    ) -> PlagResult:
        
        """ Проверка исходного кода задач на наличие в нем плагиата """

        if lang == Lang.PYTHON:
            lenght = len(candidate_info)
            plag_dict = {}
            for i in range(0, lenght):
                candidate_code = list(candidate_info[i].values())[1]
                pycheck = pycode_similar.detect([ref_code, candidate_code], 
                                          diff_method=pycode_similar.UnifiedDiff, 
                                          keep_prints=True, module_level=True)
                result = self._py_transform(pycheck[0][1].pop(0))
                plag_dict.update({list(candidate_info[i].values())[0]: result})
            plag_user_id = max(plag_dict, key=plag_dict.get)
            plag_score = max(plag_dict.values())
            plagiarism = PlagResult(
                uuid = plag_user_id, 
                result = plag_score
            )
            return plagiarism
        
        elif lang == Lang.CPP:
            result = self._sim_check(
                sim_settings = "sim_c++ -r4 -s -p  t1.cpp t2.cpp", 
                sim_lang = lang,
                ref_code = ref_code, 
                candidate_info = candidate_info
            )
            return result

        elif lang == Lang.JAVA:
            result = self._sim_check(
                sim_settings = "sim_java -r4 -s -p  t1.java t2.java", 
                sim_lang = lang,
                ref_code = ref_code, 
                candidate_info = candidate_info
            ) 
            return result        