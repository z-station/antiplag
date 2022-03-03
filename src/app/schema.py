from typing import Optional
from marshmallow import Schema, ValidationError
from marshmallow.fields import (
    Nested,
    Field,
    Boolean,
    Integer,
    Float,
    Method
)
from marshmallow.decorators import (
    post_load,
    pre_dump
)
from setuptools import Require
from app.service.entities import (
    RequestPlag,
    ResponsePlag
)
from app.service.exceptions import ServiceException

class StrField(Field):

    def _clean_str(self, value: str) -> str:
        return value.replace('\r', '').rstrip('\n')

    def _deserialize(self, value: Optional[str], *args, **kwargs):
        if isinstance(value, str):
            return self._clean_str(value)
        return value

    def _serialize(self, value: Optional[str], *args, **kwargs):
        if isinstance(value, str):
            return self._clean_str(value)
        return value

class CandidateSchema(Schema):

    uuid = Integer(required=True, load_only=True)
    code = StrField(required = True, load_only=True)

class CheckSchema(Schema):

    uuid = Integer(required=True, load_only=True)
    percent = Float(required=True, load_only=True)
    lang = StrField(required=True, load_only=True)
    ref_code = StrField(required=True, load_only=True)
    candidate_info = Nested(CandidateSchema, many=True, required=True)

class BadRequestSchema(Schema):

    error = Method('dump_error')
    details = Method('dump_details')

    def dump_error(self, obj):
        ex = obj.description
        if isinstance(ex, ServiceException):
            return ex.message
        elif isinstance(ex, ValidationError):
            return 'Validation Error'
        else:
            return 'Internal Error'

    def dump_details(self, obj):
        ex = obj.description
        if isinstance(ex, ServiceException):
            return ex.details
        elif isinstance(ex, ValidationError):
            return ex.messages
        else:
            return str(ex)