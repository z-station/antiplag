from app.services.enums import Lang
from app.services.entities import CheckInput
from app.services import exceptions
from app.services.sim.service import SimService
from app.services.pycode.service import PycodeSimilarService
from app.services.sql.service import SqlPlagService


class AntiplagService:

    service_cls_map = {
        Lang.CPP: SimService,
        Lang.JAVA: SimService,
        Lang.PYTHON: PycodeSimilarService,
        Lang.SQL: SqlPlagService,
    }

    def check(self, data: CheckInput):

        """ Проверка исходного кода задач на наличие в нем плагиата. """

        lang: str = data['lang']
        try:
            service_cls = self.service_cls_map[lang]
        except KeyError:
            raise exceptions.LanguageException()
        return service_cls().check_plagiarism(data)
