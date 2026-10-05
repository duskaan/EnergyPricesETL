import requests, pandas as pd, json
from requests.exceptions import HTTPError

testing = True

URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"

params = {'start':"StartOfDay BP1D" ,  "filter": json.dumps({"PriceArea":["DK1", "DK2"]})}
if(testing):
    params["limit"]=20
#"start=StartOfDay%2BP1D" dynamic timestamp
try:
    r = requests.get(URL, params=params, timeout=100)
    r.raise_for_status()
    #print(r.text)
except requests.exceptions.Timeout:
    print("Timed out")
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')

except Exception as err:
    print(f'error occurred: {err}')


df = pd.DataFrame(r.json())
count = df.to_records.count()
print("There are " , count, " rows")
print(df.values)

