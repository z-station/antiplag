from typing import TypedDict, List

import pycode_similar
import subprocess
import re

class Candidate(TypedDict):

    uuid: str
    code: str

class Lang:

    CPP = 'cpp'
    PYTHON = 'python'
    JAVA = 'java'

    CHOICES = (
        (CPP, CPP),
        (PYTHON, PYTHON),
        (PYTHON, PYTHON)
    )

class CappaPlag:

    def py_transform(self, data) -> int:

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
    
    def sim_transform(self, data) -> int:
        out = (re.findall(r'\b\d+\b', data))[-1]
        result = int(out)
        return result
    
    def sim_check(
        self, 
        sim_settings: str, 
        ref_code: str, 
        candidate_info: List[Candidate]
    ) -> tuple:
        
        lenght = len(candidate_info)
        plag_dict = {}
        ref = open("t1.cpp", "w+")
        ref.write(ref_code)
        for i in range(0, lenght):
            candidate_code = list(candidate_info[i].values())[1]
            with open("t2.cpp", "w+") as cand:
                cand.write(candidate_code)
                ref.close()
                cand.close()
            simcheck = subprocess.getoutput(sim_settings)
            result = self.sim_transform(simcheck)
            plag_dict.update({list(candidate_info[i].values())[0]: result})
        plag_user_id = max(plag_dict, key=plag_dict.get)
        plag_score = max(plag_dict.values())
        return plag_user_id, plag_score
    
    def check(
        self, 
        lang: Lang.CHOICES, 
        ref_code: str, 
        candidate_info: List[Candidate]
    ) -> tuple:
        
        if lang == Lang.PYTHON:
            lenght = len(candidate_info)
            plag_dict = {}
            for i in range(0, lenght):
                candidate_code = list(candidate_info[i].values())[1]
                pycheck = pycode_similar.detect([ref_code, candidate_code], 
                                          diff_method=pycode_similar.UnifiedDiff, 
                                          keep_prints=True, module_level=True)
                result = self.py_transform(pycheck[0][1].pop(1))
                plag_dict.update({list(candidate_info[i].values())[0]: result})
            plag_user_id = max(plag_dict, key=plag_dict.get)
            plag_score = max(plag_dict.values())
            return plag_user_id, plag_score
        
        elif lang == Lang.CPP:
            result = self.sim_check(
                "sim_c++ -r4 -s -p  t1.cpp t2.cpp", 
                ref_code, 
                candidate_info)
            return result

        elif lang == Lang.JAVA:
            result = self.sim_check(
                "sim_java -r4 -s -p  t1.java t2.java", 
                ref_code, 
                candidate_info)   
            return result          