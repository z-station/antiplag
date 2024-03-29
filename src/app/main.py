from flask import (
    Flask,
    request,
    render_template,
    abort
)
from marshmallow import ValidationError
from app.service.main import AntiplagService
from app.service.entities import (
    CheckResult,
    CheckInput
)
from app.schema import (
    BadRequestSchema,
    ServiceExceptionSchema,
    CheckSchema
)
from app.service.exceptions import ServiceException


def create_app():

    app = Flask(__name__)

    @app.errorhandler(400)
    def bad_request_handler(ex: ValidationError):
        return BadRequestSchema().dump(ex), 400

    @app.errorhandler(500)
    def bad_request_handler(ex: ServiceException):
        return ServiceExceptionSchema().dump(ex), 500

    @app.route('/', methods=['get'])
    def index():
        return render_template("index.html")

    @app.route('/check/', methods=['post'])
    def check() -> CheckResult:

        schema = CheckSchema()
        service = AntiplagService()
        try:
            request_data: CheckInput = request.json
            data = service.check(
                data=schema.load(request_data)
            )
        except ValidationError as ex:
            abort(400, ex)
        except ServiceException as ex:
            abort(500, ex)
        else:
            return schema.dump(data)
    return app


app = create_app()
