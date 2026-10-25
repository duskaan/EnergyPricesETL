import boto3, requests, pytest

import fetch_energinet as fetch

start, end = fetch.getParams(startDate="2026-10-04", endDate="2026-10-05")

if(start=="2026-10-04T00:00" and end =="2026-10-05T23:59"):
    print("parameter test success")
else:
    raise ValueError("daterange: start and end dates do not fit the required parameter format")

start_tomorrow, end_tomorrow = fetch.getParams(tomorrow=True)

if(start_tomorrow=="StartOfDay +P1D" and end_tomorrow =="StartOfDay +P2D"):
    print("tomorrow test success")
else:
    raise ValueError("tomorrow: start and end dates do not fit the required parameter format")

start_yesterday, end_yesterday= fetch.getParams()

if(start_yesterday=="StartOfDay-P1D" and end_yesterday =="StartOfDay"):
    print("yesterday test success")
else:
    raise ValueError("yesterday: start and end dates do not fit the required parameter format")

print("Single startdate test")
with pytest.raises(ValueError):
    fetch.getParams(startDate="2026-10-04")

#print("date range and tomorrow test")   
#with pytest.raises(ValueError):
 #   fetch.getParams(startDate="2026-10-04", endDate="2026-10-05", tomorrow=True)

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

if(set(split_data.keys())=={"2026-10-04","2026-10-05"}):
    print("split test success")
else:
    print(split_data.keys())
    raise ValueError("Records are not split according to expected output - potentially UTC is used instead of DK")

