from datetime import date, timedelta

import pendulum
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.sdk import Param, dag, task

import athena_checks
import fetch_energinet


@dag(
    dag_id="energinet_dayahead",
    start_date = pendulum.datetime(2026, 7,1, tz="Europe/Copenhagen"),
    schedule="0 14 * * *",
    catchup = False, 
    tags = ['learning'],
    params={"start_date": Param(None, type=["null", "string"], format="date"), "end_date": Param(None, type=["null", "string"], format="date")},
    default_args={"retries": 2, "retry_delay": timedelta(minutes=30)}
)


def energinet_dayahead():
    @task
    def pull_data_to_s3(params=None,ds=None):
        if(params["start_date"] and params["end_date"]):
            fetch_energinet.run(params["start_date"],params["end_date"])
            return "ALL"
        else:
            dt = (date.fromisoformat(ds) + timedelta(days=1)).isoformat()
            fetch_energinet.run(dt,dt)
            return dt
 
    @task
    def print_date(ds= None):
        print(f"The run date is {ds}")


    #@task
    #def glue_clean(target_date=None):
    #    run_glue_job = AwsGlueJobOperator(task_id="glue_clean", job_name="clean_dayaheadprices", script_args={"--date": target_date}, wait_for_completion=True, region_name="eu-central-1")
    #    run_glue_job
    
    @task
    def check_in_athena(target_date):
        athena_checks.check_day(target_date)
    
        

    target_date =pull_data_to_s3()
    glue = GlueJobOperator(task_id="glue_clean", job_name="clean_dayaheadprices", script_args={"--date": target_date}, wait_for_completion=True, region_name="eu-central-1")
    
    check = check_in_athena(target_date)
    glue >> check


energinet_dayahead()