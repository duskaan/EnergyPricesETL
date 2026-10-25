import athena_checks, pytest, boto3

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