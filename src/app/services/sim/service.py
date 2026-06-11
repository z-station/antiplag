import subprocess
import re
from typing import List

from app.services.enums import Lang
from app.services.entities import (
    Candidate,
    CheckInput,
    CheckResult
)
from app.services.utils import PlagFile
from app.services import exceptions
from app.services.base import AntiplagBaseService


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

    def _call_sim(self, cmd: str):
        return subprocess.getoutput(cmd=cmd)


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
            cmd = f'{checker_command} {reference_path} {candidate_path}'
            sim_cmd = self._call_sim(cmd=cmd)
            plag_percent = self._get_value_from_sim_console_output(sim_cmd)
            candidate_uuid = candidate['uuid']
            plag_percent_by_uuids[candidate_uuid] = plag_percent
            candidate_code_file.remove()
        reference_file.remove()
        return self._get_candidate_with_max_plag(plag_percent_by_uuids)
