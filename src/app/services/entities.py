from typing import (
    List,
    Optional,
    TypedDict,
)


class Candidate(TypedDict):

    """ Содержит данные о кандидате сравнения """

    uuid: str
    code: str


class CheckInput(TypedDict):

    """ Описывает формат запрашиваемых данных """

    lang: str
    ref_code: str
    candidates: List[Candidate]


class CheckResult(TypedDict):

    """ Описывает формат результата сравнения файлов """

    uuid: Optional[str]
    percent: float
