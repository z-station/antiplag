from flask import Flask, request
from flask import render_template
from flask_cors import CORS

from app import config

from app.service.main import AntiplagService
from app.service.entities import (
    RequestPlag,
    ResponsePlag
)

app = Flask(__name__)
CORS(app)
service = AntiplagService()


@app.route('/', methods=['get'])
def index():
    return render_template("index.html")


@app.route('/check/', methods=['post'])
def check() -> ResponsePlag:
    data: RequestPlag = request.json
    result = service.check(data)
    return result
