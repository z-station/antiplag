from typing_extensions import TypedDict
from typing import (
    List,
    Union
)


class Candidates(TypedDict):

    """ Содержит данные о кандидатах сравнения """

    uuid: str
    code: str


class CheckInput(TypedDict):

    """ Описывает формат запрашиваемых данных """

    lang: str
    ref_code: str
    candidate_info: List[Candidates]


class CheckResult(TypedDict):

    """ Описывает формат результата сравнения файлов """

    uuid: Union[int, None]
    percent: float
