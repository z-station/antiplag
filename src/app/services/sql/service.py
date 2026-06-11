import cappa_sqlplag
from app.services.entities import (
    CheckInput,
    CheckResult
)
from app.services import exceptions
from app.services.base import AntiplagBaseService


class SqlPlagService(AntiplagBaseService):

    @staticmethod
    def _get_query_type(code: str) -> str:
        normalized_code = code.lstrip().lower()

        if normalized_code.startswith('select'):
            return 'select'

        if normalized_code.startswith('with'):
            return 'with'

        return 'unknown'

    @staticmethod
    def _normalize_percent(percent: float) -> float:
        return max(0.0, min(1.0, percent / 100))

    @classmethod
    def _calculate_percent(cls, sqlplag, query_type: str) -> float:
        if query_type == 'select':
            percent = sqlplag.similarity_percentage()
        elif query_type == 'with':
            percent = sqlplag.cte_similarity_percentage()
        else:
            raise exceptions.UnsupportedQueryException()

        return cls._normalize_percent(percent)

    def check_plagiarism(self, data: CheckInput) -> CheckResult:

        """ Проверка на плагиат SQL-запросов с помощью cappa-sqlplag. """

        ref_type = self._get_query_type(data['ref_code'])

        if ref_type == 'unknown':
            raise exceptions.UnsupportedQueryException()

        plag_percent_by_uuids = {}

        for candidate in data['candidates']:
            candidate_type = self._get_query_type(candidate['code'])

            if candidate_type != ref_type:
                continue

            sqlplag = cappa_sqlplag.SQLPlag(
                ref_code=data['ref_code'],
                candidate_code=candidate['code']
            )

            plag_percent_by_uuids[candidate['uuid']] = self._calculate_percent(
                sqlplag,
                ref_type
            )

        if not plag_percent_by_uuids:
            return CheckResult(
                uuid=None,
                percent=0.0
            )

        return self._get_candidate_with_max_plag(plag_percent_by_uuids)
