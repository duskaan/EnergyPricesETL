import pytest

import fetch_energinet as fetch


def test_getparams_date_range():
    start, end = fetch.getParams(startDate="2026-10-04", endDate="2026-10-05")
    assert(start, end) == ("2026-10-04T00:00","2026-10-05T23:59")

def test_getparams_tomorrow():
    start, end = fetch.getParams(tomorrow=True)
    assert(start, end) == ("StartOfDay +P1D","StartOfDay +P2D")

def test_getparams_yesterday():
    start, end = fetch.getParams()
    assert(start, end) == ("StartOfDay-P1D","StartOfDay")

def test_getparams_singledate():
    with pytest.raises(ValueError):
        fetch.getParams(startDate="2026-10-04")

@pytest.mark.xfail(reason="getParams ignores dates when tomorrow=True")
def test_getparams_date_range_tomorrow():
    with pytest.raises(ValueError):
        fetch.getParams(startDate="2026-10-04", endDate="2026-10-05", tomorrow=True)


def test_split_records_date():

    records = [
        {
            "TimeUTC": "2026-10-03T22:00:00",
            "TimeDK": "2026-10-04T00:00:00",
            "PriceArea": "DK1",
            "DayAheadPriceEUR": 85.12,
            "DayAheadPriceDKK": 635.10,
        },
        {
            "TimeUTC": "2026-10-04T21:45:00",
            "TimeDK": "2026-10-04T23:45:00",
            "PriceArea": "DK1",
            "DayAheadPriceEUR": 92.40,
            "DayAheadPriceDKK": 689.40,
        },
        {
            "TimeUTC": "2026-10-04T22:00:00",
            "TimeDK": "2026-10-05T00:00:00",
            "PriceArea": "DK1",
            "DayAheadPriceEUR": 78.95,
            "DayAheadPriceDKK": 589.05,
        },
    ]

    split_data=fetch.split_records_by_date(records)
    assert(set(split_data.keys())=={"2026-10-04","2026-10-05"})
    assert len(split_data["2026-10-04"]) == 2
    assert len(split_data["2026-10-05"]) == 1
    