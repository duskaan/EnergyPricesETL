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
    level=logging.INFO
)
logging.debug("This is a new log.")


testing = False
parameter= {"filter": json.dumps({"PriceArea":["DK1", "DK2"]})}

def getParams(startDate=0, endDate=0, tomorrow=False): 
    """Build the start and end values for the Energinet API.

    Dates are inclusive and in Danish time: startDate="2026-10-04",
    endDate="2026-10-05" returns two full days.

    Args:
        startDate: First day as "YYYY-MM-DD". Use together with endDate.
        endDate: Last day as "YYYY-MM-DD", inclusive.
        tomorrow: If True, return tomorrow's day. Don't combine with dates.

    Returns:
        A (start, end) tuple of strings for the API's start and end parameters.

    Raises:
        ValueError: If the combination of arguments isn't valid.
    """
    start = ''
    end = ''
    if(tomorrow):
        start='StartOfDay +P1D'
        end='StartOfDay +P2D'
    elif(startDate!=0 and endDate!=0):
        start=f'{startDate}T00:00'
        end=f'{endDate}T23:59'

    elif(startDate==0 and endDate==0 and tomorrow==False):
        start='StartOfDay-P1D'
        end='StartOfDay'
    else:
        raise Exception("This is not a valid date you have provided")

    return start, end

#https://api.energidataservice.dk/dataset/DayAheadPrices?offset=0&start=2026-10-06T00:00&end=2026-10-06T23:59&sort=TimeUTC%20DESC

#parameter["start"], parameter["end"] = getParams() #Yesterday
#parameter["start"], parameter["end"] = getParams(startDate=f'{start_date}T00:00', endDate='{end_date}T23:59') #full days based on variable from airflow
parameter["start"], parameter["end"] = getParams(startDate='2026-10-06', endDate='2026-10-06')
#if i need to use a specific date everytime and just want to take Airflows date -> then use this from datetime import datetime datetime.today().strftime('%Y-%m-%d')




URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"

if(testing):
    parameter["limit"]=20
try:
    r = requests.get(URL, params=parameter, timeout=30)
    r.raise_for_status()
    #print(r.text)
    
    df = pd.DataFrame(r.json()['records'])
    count = len(df)
    if(count==0):
        raise ValueError("There are no records for the choosen day, select a different date range or try again after .. o clock")
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





