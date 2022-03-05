# TODO Подключи PEP8 плагин в свой редактор чтобы он тебе подчеркнул все нарушения code style и исправь
# TODO удалить неиспользуемые импорты
# TODO удалить все комментарии - если боишься что-то потерять то для этого история git в которой все есть.
from urllib import response
from flask import (
    Flask, 
    request,
    render_template,
    abort
)

# from flask_cors import CORS
from marshmallow import ValidationError
from app import config
from app.service.main import AntiplagService
# from app.service.entities import (
#     RequestPlag,
#     ResponsePlag
# )
from app.schema import (
    CheckSchema,
    BadRequestSchema
)
from app.service.exceptions import ServiceException


def create_app():

    app = Flask(__name__)

    @app.errorhandler(400)
    def bad_request_handler(ex: Exception):
        return BadRequestSchema().dump(ex), 400
    
    @app.route('/', methods=['get'])
    def index():
        return render_template("index.html")

    @app.route('/check/', methods=['post'])
    def check():
        schema = CheckSchema()
        # TODO следи за неймингом переменных. что значит info? service более удачное название
        info = AntiplagService()
        try:
            # TODO метод check принимает аргумент типа RequestPlag
            #  а schema.load возварщает просто словарь,
            #  будет правильнее если schema.load будет возвращать инстанс RequestPlag
            data = info.check(
                data = schema.load(request.get_json())
            )
        except (ServiceException, ValidationError) as ex:
            abort(400, ex)
        else:
            return schema.dump(data)
    return app

app = create_app()

# app = Flask(__name__)
# CORS(app)
# service = AntiplagService()


# @app.route('/', methods=['get'])
# def index():
#     return render_template("index.html")


# @app.route('/check/', methods=['post'])
# def check() -> ResponsePlag:
#     data: RequestPlag = request.json
#     result = service.check(data)
#     return result
