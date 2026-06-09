from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.schema import (
    CheckRequest,
    CheckResponse,
    format_validation_errors,
)
from app.service.exceptions import ServiceException
from app.service.main import AntiplagService

APP_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=APP_DIR / 'templates')


def create_app() -> FastAPI:
    app = FastAPI()

    static_dir = APP_DIR / 'static'
    if static_dir.is_dir():
        app.mount('/static', StaticFiles(directory=static_dir), name='static')

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'Validation Error',
                'details': format_validation_errors(exc),
            },
        )

    @app.exception_handler(ServiceException)
    async def service_handler(
        request: Request,
        exc: ServiceException,
    ):
        return JSONResponse(
            status_code=500,
            content={
                'error': exc.message,
                'details': exc.details,
            },
        )

    @app.get('/')
    def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name='index.html',
        )

    @app.post('/check/', response_model=CheckResponse)
    def check(body: CheckRequest) -> CheckResponse:
        result = AntiplagService().check(data=body.to_check_input())
        return CheckResponse(**result)

    return app


app = create_app()
