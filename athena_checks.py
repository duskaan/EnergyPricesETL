import os, time, boto3,logging, sys

def run_athena_query(sql):
    logging.info("The sql query is "+sql)
    
    athena = boto3.client("athena", region_name="eu-central-1")
    bucket = os.environ["S3_BUCKET"]
    query_id = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": "energinet"},
        ResultConfiguration={"OutputLocation": f"s3://{bucket}/athena-results/"},
        WorkGroup="primary",
    )["QueryExecutionId"]

    while True:
        state = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]
        if state["State"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)

    logging.info("The state is " +state["State"])
                 
    if state["State"] != "SUCCEEDED":
        raise RuntimeError(f"Athena query {state['State']}: {state.get('StateChangeReason')}")
    return athena.get_query_results(QueryExecutionId=query_id)

def check_day(price_date):
    if price_date == "ALL":
        sql_partition = "MSCK REPAIR TABLE dayaheadprices"
        where_clause =""
       
        
    else:
        sql_partition = f"""ALTER TABLE energinet.dayaheadprices ADD IF NOT EXISTS PARTITION (price_date = '{price_date}')"""
        where_clause =  f"where price_date = '{price_date}'"

    sql_check =  f"""SELECT
                        count_if(n NOT IN (184, 192, 200)) AS bad_days,
                        count(*)                           AS days_found
                    FROM (
                        SELECT price_date, count(*) AS n
                        FROM energinet.dayaheadprices
                        {where_clause}
                        GROUP BY price_date
                    )"""
    
    results2 = run_athena_query(sql_partition)
    print(results2)
    check_result = run_athena_query(sql_check)
    print(check_result)
    count_bad_days= int(check_result["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"])
    count_days_found= int(check_result["ResultSet"]["Rows"][1]["Data"][1]["VarCharValue"])

    if count_bad_days==0 and count_days_found>0:
        logging.info("The query succeeded")
    else:
        raise ValueError(f"Expected 184, 192 or 200 rows for {price_date}, got {count_bad_days} bad day and total of {count_days_found} days found")

if __name__ == '__main__':
    #Set logging config 
    logging.basicConfig(
        #filename="app.log",
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
    check_day(sys.argv[1])