import fetch_energinet
import pendulum
from datetime import  timedelta, date
from airflow.sdk import dag, task, Param

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
        else:
            dt = (date.fromisoformat(ds) + timedelta(days=1)).isoformat()
            fetch_energinet.run(dt,dt)

    @task
    def print_date(ds= None):
        print(f"The run date is {ds}")

    pull_data_to_s3() >> print_date()

energinet_dayahead()