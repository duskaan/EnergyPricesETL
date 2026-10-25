import pytest

import athena_checks


def test_check_day_raises_when_no_data(monkeypatch):
    def fake_query(sql):
        # same shape as Athena: header row, then one data row (bad_days, days_found)
        return {"ResultSet": {"Rows": [
            {"Data": [{"VarCharValue": "bad_days"}, {"VarCharValue": "days_found"}]},
            {"Data": [{"VarCharValue": "0"}, {"VarCharValue": "0"}]},
        ]}}

    monkeypatch.setattr(athena_checks, "run_athena_query", fake_query)

    with pytest.raises(ValueError):
        athena_checks.check_day("2026-10-04")

def test_check_day_raises_when_bad_data(monkeypatch):
    def fake_query(sql):
        # same shape as Athena: header row, then one data row (bad_days, days_found)
        return {"ResultSet": {"Rows": [
            {"Data": [{"VarCharValue": "bad_days"}, {"VarCharValue": "days_found"}]},
            {"Data": [{"VarCharValue": "1"}, {"VarCharValue": "1"}]},
        ]}}

    monkeypatch.setattr(athena_checks, "run_athena_query", fake_query)

    with pytest.raises(ValueError):
        athena_checks.check_day("2026-10-04")

def test_check_day_succeeds_when_good_data(monkeypatch):
    def fake_query(sql):
        # same shape as Athena: header row, then one data row (bad_days, days_found)
        return {"ResultSet": {"Rows": [
            {"Data": [{"VarCharValue": "bad_days"}, {"VarCharValue": "days_found"}]},
            {"Data": [{"VarCharValue": "0"}, {"VarCharValue": "1"}]},
        ]}}

    monkeypatch.setattr(athena_checks, "run_athena_query", fake_query)
    
    athena_checks.check_day("2026-10-04")
