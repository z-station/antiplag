import pytest
from app.services import messages
from app.services.main import SqlPlagService
from app.services.enums import Lang
from app.services.entities import (
    CheckInput,
    CheckResult,
    Candidate,
)

from app.services.exceptions import UnsupportedQueryException


def test_check_plagiarism__select_queries__ok(mocker):

    # arrange
    ref_code = 'SELECT 1'
    candidate_code = 'SELECT 2'
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )
    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'select']
    )
    plag_percent = 0.82
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    expected_result = CheckResult(uuid='candidate-1', percent=plag_percent)
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    get_query_type_mock.assert_any_call(ref_code)
    get_query_type_mock.assert_any_call(candidate_code)
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-1': plag_percent}
    )
    assert result == expected_result


def test_check_plagiarism__cte_queries__ok(mocker):

    # arrange
    ref_code = 'WITH t AS (SELECT 1) SELECT * FROM t'
    candidate_code = 'WITH t AS (SELECT 2) SELECT * FROM t'
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )
    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['with', 'with']
    )
    plag_percent = 0.9
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    expected_result = CheckResult(uuid='candidate-1', percent=plag_percent)
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    get_query_type_mock.assert_any_call(ref_code)
    get_query_type_mock.assert_any_call(candidate_code)
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-1': plag_percent}
    )
    assert result == expected_result


def test_check_plagiarism__unsupported_ref_query__raise_exception(mocker):

    # arrange
    ref_code = 'INSERT INTO users VALUES (1)'
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(
                uuid='candidate-1',
                code='INSERT INTO users VALUES (2)'
            ),
        ]
    )

    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        return_value='unknown'
    )

    service = SqlPlagService()

    # act
    with pytest.raises(UnsupportedQueryException) as ex:
        service.check_plagiarism(test_data)

    # assert
    get_query_type_mock.assert_called_once_with(ref_code)
    assert ex.value.message == messages.MSG_5


def test_check_plagiarism__skip_candidates_with_other_type(mocker):

    # arrange
    ref_code = 'SELECT 1 * FROM t'
    candidate_1_code = 'WITH t AS (SELECT 1) SELECT * FROM t'
    candidate_2_code = 'SELECT 2 * FROM t'
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_1_code),
            Candidate(uuid='candidate-2', code=candidate_2_code),
        ]
    )

    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'with', 'select']
    )
    plag_percent = 0.76
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    expected_result = CheckResult(uuid='candidate-2', percent=plag_percent)
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    assert get_query_type_mock.call_count == 3
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-2': plag_percent}
    )
    assert result == expected_result


def test_check_plagiarism__different_code__min_plagiarism(mocker):

    # arrange
    ref_code = 'SELECT 1'
    candidate_code = 'WITH t AS (SELECT 1) SELECT * FROM t'
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )

    # типы не совпадают → cappa_sqlplag не вызывается → возвращает (None, 0.0)
    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'with']
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    assert get_query_type_mock.call_count == 2
    assert result == CheckResult(uuid=None, percent=0.0)


def test_check_plagiarism__identical_select_queries__max_plag(mocker):

    # arrange
    ref_code = (
        'SELECT u.id, u.name, o.total '
        'FROM users u '
        'JOIN orders o ON o.user_id = u.id '
        'WHERE o.total > 100 '
        'ORDER BY o.total DESC'
    )
    candidate_code = ref_code
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )
    expected_result = CheckResult(uuid='candidate-1', percent=1.0)

    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'select']
    )
    plag_percent = 1.0
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    assert get_query_type_mock.call_count == 2
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-1': plag_percent}
    )
    assert result == expected_result


def test_check_plagiarism__different_query__min_plagiarism(mocker):

    # arrange
    ref_code = (
        'SELECT u.id, u.name, o.total '
        'FROM users u '
        'JOIN orders o ON o.user_id = u.id '
        'WHERE o.total > 100 '
        'ORDER BY o.total DESC'
    )
    candidate_code = (
        'SELECT '
        '   department_id, '
        '   COUNT(*) AS employee_count, '
        '   AVG(salary) AS avg_salary '
        'FROM employees '
        'WHERE hire_date >= \'2020-01-01\' '
        'GROUP BY department_id '
        'HAVING COUNT(*) > 5'
    )
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )
    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'select']
    )
    plag_percent = 0.1
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    expected_result = CheckResult(uuid=None, percent=plag_percent)
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    assert get_query_type_mock.call_count == 2
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-1': plag_percent}
    )
    assert result == expected_result


def test_check_plagiarism__same_queries__partial_plagiarism(mocker):
    """
    Один и тот же результат реализован кардинально разными способами:
    - эталон: фильтрация через IN + подзапрос
    - кандидат: то же самое через JOIN

    Ожидаем промежуточный процент: сходство есть, но не 100%.
    """

    # arrange
    ref_code = (
        'SELECT id, name, email '
        'FROM users '
        'WHERE id IN ('
        '    SELECT user_id FROM orders WHERE total > 500'
        ')'
    )
    candidate_code = (
        'SELECT u.id, u.name, u.email '
        'FROM users u '
        'JOIN orders o ON o.user_id = u.id '
        'WHERE o.total > 500'
    )
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code=ref_code,
        candidates=[
            Candidate(uuid='candidate-1', code=candidate_code),
        ]
    )
    get_query_type_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._get_query_type',
        side_effect=['select', 'select']
    )
    plag_percent = 0.25
    calculate_percent_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._calculate_percent',
        return_value=plag_percent
    )
    expected_result = CheckResult(uuid='candidate-1', percent=plag_percent)
    get_candidate_with_max_plag_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService'
        '._get_candidate_with_max_plag',
        return_value=expected_result
    )

    service = SqlPlagService()

    # act
    result = service.check_plagiarism(test_data)

    # assert
    assert get_query_type_mock.call_count == 2
    calculate_percent_mock.assert_called_once()
    get_candidate_with_max_plag_mock.assert_called_once_with(
        {'candidate-1': plag_percent}
    )
    assert result == expected_result


# --- _get_query_type ---

def test_get_query_type__select__ok():
    assert SqlPlagService._get_query_type('SELECT 1') == 'select'


def test_get_query_type__select_leading_spaces__ok():
    assert SqlPlagService._get_query_type('  SELECT 1') == 'select'


def test_get_query_type__select_uppercase__ok():
    assert SqlPlagService._get_query_type('SELECT id FROM t') == 'select'


def test_get_query_type__cte__ok():
    query = 'WITH t AS (SELECT 1) SELECT * FROM t'
    assert SqlPlagService._get_query_type(query) == 'with'


def test_get_query_type__insert__unknown():
    query = 'INSERT INTO users VALUES (1)'
    assert SqlPlagService._get_query_type(query) == 'unknown'


def test_get_query_type__empty_string__unknown():
    assert SqlPlagService._get_query_type('') == 'unknown'


# --- _normalize_percent ---

def test_normalize_percent__normal_value__ok():
    assert SqlPlagService._normalize_percent(82.0) == 0.82


def test_normalize_percent__exactly_100__ok():
    assert SqlPlagService._normalize_percent(100.0) == 1.0


def test_normalize_percent__zero__ok():
    assert SqlPlagService._normalize_percent(0.0) == 0.0


def test_normalize_percent__over_100__clamped_to_1():
    assert SqlPlagService._normalize_percent(110.0) == 1.0


def test_normalize_percent__negative__clamped_to_0():
    assert SqlPlagService._normalize_percent(-5.0) == 0.0


# --- _calculate_percent ---

def test_calculate_percent__select__calls_similarity_pct(mocker):

    # arrange
    sqlplag_mock = mocker.Mock()
    sqlplag_mock.similarity_percentage.return_value = 82.0

    normalize_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._normalize_percent',
        return_value=0.82
    )

    # act
    result = SqlPlagService._calculate_percent(
        sqlplag=sqlplag_mock,
        query_type='select'
    )

    # assert
    sqlplag_mock.similarity_percentage.assert_called_once()
    normalize_mock.assert_called_once_with(82.0)
    assert result == 0.82


def test_calculate_percent__with__calls_cte_similarity_pct(mocker):

    # arrange
    sqlplag_mock = mocker.Mock()
    sqlplag_mock.cte_similarity_percentage.return_value = 90.0

    normalize_mock = mocker.patch(
        'app.services.sql.service.SqlPlagService._normalize_percent',
        return_value=0.9
    )

    # act
    result = SqlPlagService._calculate_percent(
        sqlplag=sqlplag_mock,
        query_type='with'
    )

    # assert
    sqlplag_mock.cte_similarity_percentage.assert_called_once()
    normalize_mock.assert_called_once_with(90.0)
    assert result == 0.9


def test_calculate_percent__unknown_type__raise_exception(mocker):

    # arrange
    sqlplag_mock = mocker.Mock()

    # act
    with pytest.raises(UnsupportedQueryException):
        SqlPlagService._calculate_percent(
            sqlplag=sqlplag_mock,
            query_type='unknown'
        )

    # assert
    sqlplag_mock.similarity_percentage.assert_not_called()
    sqlplag_mock.cte_similarity_percentage.assert_not_called()
