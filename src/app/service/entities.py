from typing_extensions import TypedDict
from typing import List
from enums import Lang


class Candidate(TypedDict):

    """ Содержит данные о кандидатах сравнения. """

    uuid: str
    code: str


class PlagResult(TypedDict):

    """ Описывает формат результата сравнения файлов. """

    uuid: str
    result: int
