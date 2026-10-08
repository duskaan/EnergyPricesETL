import sys

import requests, pandas as pd, json
from requests.exceptions import HTTPError
from collections import defaultdict
import boto3
#from botocore.exceptions import ClientError


import os
from dotenv import load_dotenv
#get env variables
load_dotenv()
BUCKET = os.environ["S3_BUCKET"]

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
        raise ValueError("This is not a valid date you have provided")

    return start, end

#https://api.energidataservice.dk/dataset/DayAheadPrices?offset=0&start=2026-10-06T00:00&end=2026-10-06T23:59&sort=TimeUTC%20DESC

def call_API(URL, parameter):
    r = requests.get(URL, params=parameter, timeout=30)
    r.raise_for_status()
    return r.json()['records']

def split_records_by_date(json_records):
    split_by_date = defaultdict(list)

    for record in json_records:
        split_by_date[record['TimeDK'][:10]].append(record)

    logging.info(split_by_date.keys())
    return split_by_date

def run(start_date, end_date):
    parameter["start"], parameter["end"] = getParams(startDate=start_date, endDate=end_date)

    #parameter["start"], parameter["end"] = getParams(tomorrow=True)
    #parameter["start"], parameter["end"] = getParams() #Yesterday
    #parameter["start"], parameter["end"] = getParams(startDate=f'{start_date}', endDate='{end_date}') #full days based on variable from airflow
    #parameter["start"], parameter["end"] = getParams(startDate='2026-09-25', endDate='2026-10-06')
    #if i need to use a specific date everytime and just want to take Airflows date -> then use this from datetime import datetime datetime.today().strftime('%Y-%m-%d')
    URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"

    if(testing):
        parameter["limit"]=20
    try:
        
        json_records = call_API(URL, parameter)
    
        count = len(json_records)
        if(count==0):
            raise ValueError("There are no records for the choosen day, select a different date range or try again after .. o clock")
        #time_stamp = r.json()['records'][0]['TimeDK'].split('T',1)[0]
    
        
        records_by_date = split_records_by_date(json_records)


        s3 = boto3.client('s3')

        for date,records in records_by_date.items():
            file_name = f'raw/dayaheadprices/date={date}/dayaheadprices.json'

            #create file here for that specific date
            #s3object = s3.Object(BUCKET, file_name)
            s3.put_object(
                Bucket=BUCKET,
                Key=file_name,
                Body=(json.dumps(records).encode('UTF-8')),
                ContentType='application/json'
            )
            logging.info(f"I uploaded a file to the path {file_name} with {len(records)} records")

        #logging.info(f"There are {count} rows and the following values {df.head()}")
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




if __name__ == '__main__':
    run(sys.argv[1],sys.argv[2])


