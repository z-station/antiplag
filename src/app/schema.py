from marshmallow import Schema, validate
from marshmallow.fields import (
    Nested,
    Integer,
    Float,
    String,
    Method
)
from marshmallow.decorators import (
    post_load,
)
from app.service.entities import (
    Candidate,
    CheckInput,
)
from app.service.enums import Lang


class CandidateSchema(Schema):

    uuid = String(required=True, load_only=True)
    code = String(required=True, load_only=True)

    @post_load
    def make_candidate_data(self, data, **kwargs) -> Candidate:
        return Candidate(**data)


class CheckSchema(Schema):

    lang = String(
        load_only=True,
        required=True,
        validate=validate.OneOf(Lang.VALUES)
    )
    ref_code = String(required=True, load_only=True)
    candidates = Nested(CandidateSchema, many=True, required=True)

    uuid = String(dump_only=True)
    percent = Float(dump_only=True)

    @post_load
    def make_check_data(self, data, **kwargs) -> CheckInput:
        return CheckInput(**data)


class BadRequestSchema(Schema):

    error = Method('dump_error')
    details = Method('dump_details')

    def dump_error(self, obj):
        return 'Validation Error'

    def dump_details(self, obj):
        return obj.description.messages


class ServiceExceptionSchema(Schema):

    error = Method('dump_error')
    details = Method('dump_details')

    def dump_error(self, obj):
        return obj.description.message

    def dump_details(self, obj):
        return obj.description.details
