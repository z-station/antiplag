import pytest
from app.services.main import SqlPlagService
from app.services.enums import Lang
from app.services.entities import (
    CheckInput,
    CheckResult,
    Candidate,
)

from app.services.exceptions import UnsupportedQueryException


def test_check_plagiarism__select_queries__ok():
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code='SELECT 1',
        candidates=[
            Candidate(uuid='candidate-1', code='SELECT 2'),
        ]
    )


    service = SqlPlagService()
    result = service.check_plagiarism(test_data)

    assert result == CheckResult(uuid='candidate-1', percent=0.82)


def test_check_plagiarism__cte_queries__ok():
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code='WITH t AS (SELECT 1) SELECT * FROM t',
        candidates=[
            Candidate(
                uuid='candidate-1',
                code='WITH t AS (SELECT 2) SELECT * FROM t'
            ),
        ]
    )

    service = SqlPlagService()
    result = service.check_plagiarism(test_data)

    assert result == CheckResult(uuid='candidate-1', percent=0.9)


def test_check_plagiarism__unsupported_ref_query__raise_exception():
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code='INSERT INTO users VALUES (1)',
        candidates=[
            Candidate(
                uuid='candidate-1',
                code='INSERT INTO users VALUES (2)'
            ),
        ]
    )

    service = SqlPlagService()

    with pytest.raises(UnsupportedQueryException):
        service.check_plagiarism(test_data)


def test_check_plagiarism__skip_candidates_with_other_query_type():
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code='SELECT 1',
        candidates=[
            Candidate(
                uuid='candidate-1',
                code='WITH t AS (SELECT 1) SELECT * FROM t'
            ),
            Candidate(uuid='candidate-2', code='SELECT 2'),
        ]
    )

    service = SqlPlagService()
    result = service.check_plagiarism(test_data)

    assert result == CheckResult(uuid='candidate-2', percent=0.82)


def test_check_plagiarism__no_matching_candidates__return_zero():
    test_data = CheckInput(
        lang=Lang.SQL,
        ref_code='SELECT 1',
        candidates=[
            Candidate(
                uuid='candidate-1',
                code='WITH t AS (SELECT 1) SELECT * FROM t'
            ),
        ]
    )

    service = SqlPlagService()
    result = service.check_plagiarism(test_data)

    assert result == CheckResult(uuid=None, percent=0.0)
