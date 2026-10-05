import requests, pandas as pd, json
from requests.exceptions import HTTPError

testing = False

URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"
#tomorrow
#params = {'start':"StartOfDay BP1D" ,  "filter": json.dumps({"PriceArea":["DK1", "DK2"]})}
#yesterday
params = {"start": "StartOfDay-P1D",
    "end": "StartOfDay",
    "filter": json.dumps({"PriceArea":["DK1", "DK2"]})
    }

if(testing):
    params["limit"]=20
#"start=StartOfDay%2BP1D" dynamic timestamp
try:
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    #print(r.text)
    
    df = pd.DataFrame(r.json()['records'])
    count = len(df)
    print("There are " , count, " rows")
    print(df.values)
except requests.exceptions.Timeout:
    print("Timed out")
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')

except Exception as err:
    print(f'error occurred: {err}')




