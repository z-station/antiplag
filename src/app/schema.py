from marshmallow import Schema
from marshmallow.fields import (
    Nested,
    Integer,
    Float,
    String
)
from marshmallow.decorators import (
    post_load,
)
from app.service.entities import (
    Candidates,
    CheckInput,
)


class CandidateSchema(Schema):

    uuid = Integer(required=True, load_only=True)
    code = String(required=True, load_only=True)

    @post_load
    def make_candidate_data(self, data, **kwargs) -> Candidates:
        return Candidates(**data)


class CheckSchema(Schema):

    lang = String(required=True, load_only=True)
    ref_code = String(required=True, load_only=True)
    candidate_info = Nested(CandidateSchema, many=True, required=True)

    uuid = Integer(dump_only=True)
    percent = Float(dump_only=True)

    @post_load
    def make_check_data(self, data, **kwargs) -> CheckInput:
        return CheckInput(**data)
