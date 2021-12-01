from typing_extensions import TypedDict
from typing import List


class Candidates(TypedDict):

    """ Содержит данные о кандидатах сравнения """

    uuid: str
    code: str


class RequestPlag(TypedDict):

    """ Описывает формат запрашиваемых данных """

    lang: str
    ref_code: str
    candidate_info: List[Candidates]


class ResponsePlag(TypedDict):

    """ Описывает формат результата сравнения файлов """

    uuid: int
    percent: int
