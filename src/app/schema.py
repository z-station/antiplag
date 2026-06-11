from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator

from app.services.entities import CheckInput
from app.services.enums import Lang


class CandidateModel(BaseModel):
    uuid: str
    code: str


class CheckRequest(BaseModel):
    lang: str
    ref_code: str
    candidates: list[CandidateModel]

    @field_validator('lang')
    @classmethod
    def validate_lang(cls, value: str) -> str:
        if value not in Lang.VALUES:
            raise ValueError('Must be one of: cpp, java, python, sql.')
        return value

    def to_check_input(self) -> CheckInput:
        return CheckInput(
            lang=self.lang,
            ref_code=self.ref_code,
            candidates=[
                {'uuid': candidate.uuid, 'code': candidate.code}
                for candidate in self.candidates
            ],
        )


class CheckResponse(BaseModel):
    uuid: str | None
    percent: float


class BadRequestResponse(BaseModel):
    error: str
    details: dict[str, list[str]]


class ServiceErrorResponse(BaseModel):
    error: str
    details: str | None


def format_validation_errors(exc: RequestValidationError) -> dict[str, list[str]]:
    details: dict[str, list[str]] = {}
    for error in exc.errors():
        loc = error['loc']
        if loc and loc[0] == 'body':
            loc = loc[1:]
        field = '.'.join(str(part) for part in loc) if loc else '__root__'
        message = error['msg']
        if message == 'Field required':
            message = 'Missing data for required field.'
        elif message.startswith('Value error, '):
            message = message.removeprefix('Value error, ')
        details.setdefault(field, []).append(message)
    return details
