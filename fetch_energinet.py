import requests, json, boto3, sys, os, logging
from requests.exceptions import HTTPError
from collections import defaultdict

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

def save_to_s3(bucket, records_by_date):
    s3 = boto3.client('s3')
    
    for date,records in records_by_date.items():
        file_name = f'raw/dayaheadprices/date={date}/dayaheadprices.json'

        #create file here for that specific date
        s3.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=(json.dumps(records).encode('UTF-8')),
            ContentType='application/json'
        )
        logging.info(f"I uploaded a file to the path {file_name} with {len(records)} records")

def run(start_date, end_date):
    BUCKET = os.environ["S3_BUCKET"]
    
    testing = False
    parameter= {"filter": json.dumps({"PriceArea":["DK1", "DK2"]})}
    
    parameter["start"], parameter["end"] = getParams(startDate=start_date, endDate=end_date)

    #parameter["start"], parameter["end"] = getParams(tomorrow=True) #Tomorrow
    #parameter["start"], parameter["end"] = getParams() #Yesterday
    #parameter["start"], parameter["end"] = getParams(startDate='2026-09-25', endDate='2026-10-06') #select dates

    URL = "https://api.energidataservice.dk/dataset/DayAheadPrices"

    if(testing):
        parameter["limit"]=20
    try:
        
        json_records = call_API(URL, parameter)
    
        if(len(json_records)==0):
            raise ValueError("There are no records for the choosen day(s), select a different date range or try again after .. o clock")
    
        records_by_date = split_records_by_date(json_records)
        save_to_s3(records_by_date=records_by_date, bucket=BUCKET)

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
    #Set logging config 
    logging.basicConfig(
        filename="app.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO
    )
    #get env variables
    from dotenv import load_dotenv
    load_dotenv()

    run(sys.argv[1],sys.argv[2])

