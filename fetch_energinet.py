import requests, pandas as pd, json
from requests.exceptions import HTTPError
#logging
import logging
logging.basicConfig(
    filename="app.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG
)
logging.debug("This is a new log.")


testing = False
parameter= {"filter": json.dumps({"PriceArea":["DK1", "DK2"]})}

def getParams(startDate=0, endDate=0, tomorrow=False): 
    start = ''
    end = ''
    if(tomorrow):
        start='StartOfDay BP1D'
        end=''
    elif(startDate!=0&endDate!=0):
        start=startDate
        end=endDate

    elif(startDate==0&endDate==0&tomorrow==False):
        start='StartOfDay-P1D'
        end='StartOfDay'
    else:
        raise Exception("This is not a valid date you have provided")

    return start, end

#https://api.energidataservice.dk/dataset/DayAheadPrices?offset=0&start=2026-10-06T00:00&end=2026-10-06T23:59&sort=TimeUTC%20DESC

parameter["start"], parameter["end"] = getParams() #Yesterday
#parameter["start"], parameter["end"] = getParams(startDate=f'{start_date}T00:00', endDate='{end_date}T23:59') #full days based on variable from airflow
#parameter["start"], parameter["end"] = getParams(startDate='2026-10-06T00:00', endDate=f'2026-10-06T23:59')
#if i need to use a specific date everytime and just want to take Airflows date -> then use this from datetime import datetime datetime.today().strftime('%Y-%m-%d')

#parameter["start"], parameter["end"] = getParams(tomorrow=True) #Tomorrow
#parameter["start"] = f'{start_date}T00:00'
#parameter["end"] = f'2026-10-06T23:59'


URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"
#tomorrow
#params = {'start':"StartOfDay BP1D" ,  "filter": json.dumps({"PriceArea":["DK1", "DK2"]})}
#yesterday
'''
params = {"start": "StartOfDay-P1D",
    "end": "StartOfDay",
    "filter": json.dumps({"PriceArea":["DK1", "DK2"]})
    }
'''
if(testing):
    parameter["limit"]=20
#"start=StartOfDay%2BP1D" dynamic timestamp
try:
    r = requests.get(URL, params=parameter, timeout=30)
    r.raise_for_status()
    #print(r.text)
    
    df = pd.DataFrame(r.json()['records'])
    count = len(df)
    if(count==0):
        raise Exception("There are no records for the choosen day, select a different date range or try again after .. o clock")
    logging.info(f"There are {count} rows and the following values {df.head()}")
except requests.exceptions.Timeout:
    logging.exception("Timed out")
    raise
except HTTPError as http_err:
    logging.exception(f'HTTP error occurred: {http_err}')
    raise
except Exception as err:
    #logging.exception(err)
    logging.exception('Error occurred')
    raise 





