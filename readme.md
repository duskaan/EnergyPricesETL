# EnergyPricesETL

## Project purpose

This is a hands-on learning project: an end-to-end data pipeline built from scratch on AWS,
to learn data engineering by doing it rather than only following courses.
It covers the full path a real pipeline takes: extracting from a public API, landing raw data,
cleaning it with Spark, validating it, and orchestrating every step with Airflow,
with the decisions behind each step written down.
It runs on managed AWS services (S3, Glue, Glue Data Catalog, Athena) with least-privilege IAM roles.

The data is Energinet's day-ahead electricity prices for Denmark: the price per
quarter-hour, set the day before, for the two Danish price areas (DK1 West, DK2 East).
It is public, updated daily, and has real-world quirks worth handling properly

## What the data is meant to show

The pipeline produces a clean, validated table of prices that answers questions like:

- **When during the day is electricity expensive or cheap?** The daily shape, with morning
  and evening peaks and the midday dip from solar power.
- **How do prices change across the year?** Monthly averages, and how winter months
  compare with summer months.
- **How do the two price areas differ?** DK1 and DK2 are separate markets
  and do not always move together.
- **How often are prices negative?** Periods when supply is so high that sellers pay buyers to take the power.

Planned next: adding Energinet's CO2 emission data, so the same table can answer
*when is electricity both cheap and clean?*

## What the first year of data shows

The data covers October 2025 to 20 October 2026: one year of 15-minute prices.
October 2026 is a partial month.

### The average price has roughly doubled, but the monthly average hides most of the movement

![Average price per kWh by month](docs/images/price-avg-monthly.png)

On its own, the monthly average looks like a steep climb: from about 0.6 kr/kWh in October 2025
to about 1.25 kr/kWh in October 2026, with most of the rise since July 2026.
Part of the steep look comes from the chart's axis, which does not start at zero.

![Average price per kWh by month, with the lowest and highest quarter-hour price](docs/images/price-avg-range-monthly.png)

Putting the lowest and highest quarter-hour price of each month next to the average changes the picture.
Within any single month, prices swing from around or below zero to 5–12 kr/kWh.
That spread is many times larger than the change in the monthly average over the whole year.
The increase in the average is real, but for anyone who can shift consumption between hours,
*when* electricity is used matters far more than *which month* it is.

### Negative prices follow the sun, and were much rarer this October

![Quarter-hours with negative prices per month, DK1 and DK2 combined](docs/images/negative-quarter-hours.png)

Negative prices cluster in spring and summer (March–September), when solar and wind output is high,
and disappear completely from November to February.
October 2025 had around 180 negative quarter-hours; October 2026 has had only about 7 so far.
Even allowing for the month being two-thirds over, that is a large drop.

## Architecture

```mermaid
flowchart LR
    api["Energinet API<br/>DayAheadPrices · 15 min"]
    co2["Energinet API<br/>CO2Emis · 5 min"]:::planned
    raw[("S3 raw/<br/>JSON Lines, one file per day")]
    clean[("S3 clean/<br/>Parquet by price_date")]
    athena["Glue Data Catalog + Athena<br/>row-count check per day"]
    dbt["dbt<br/>staging + marts"]:::planned
    wh[("Warehouse<br/>Redshift or Fabric")]:::planned

    api -- "① pull_data_to_s3<br/>Python" --> raw
    co2 -. "extract" .-> raw
    raw -- "② glue_clean<br/>Glue Spark job" --> clean
    clean -- "③ check_in_athena" --> athena
    athena -. "④ dbt build" .-> dbt
    dbt -. "load / models" .-> wh

    classDef planned stroke-dasharray: 5 5,color:#777,stroke:#999
```

Solid = running today. Dashed = planned. Steps ①–④ are tasks in one Airflow DAG
(local Docker, daily at 14:00 Danish time, 2 retries).

![The Airflow DAG: extract, Glue clean, Athena check](docs/images/airflow-graph.png)

- **Schedule:** daily at 14:00 Danish time, fetching *tomorrow's* prices (published around 13:00).
- **Manual runs:** trigger with `start_date` / `end_date` params to backfill a range.

## Repository

| Path | What it is |
|---|---|
| `fetch_energinet.py` | Extract: calls the API for a date range, writes one JSON Lines file per Danish day to S3 |
| `athena_checks.py` | Validation: registers the day in the Data Catalog and fails if it is missing or has an unexpected row count |
| `dags/energinet_dayahead.py` | The Airflow DAG: extract → Glue → check |
| `glue/clean_dayaheadprices.py` | Glue Spark job: raw JSON → typed, deduplicated Parquet, for one date or `ALL` |

## Running it

Prerequisites: Docker Desktop, an AWS account, Python 3 for local runs.

1. **AWS:** an S3 bucket in `eu-central-1`, the Glue job `clean_dayaheadprices`, a Glue database `energinet`,
   and the IAM roles described under *Design decisions*.
2. **Local run** of a single step (Windows cmd):
   ```
   copy .env.example .env          & rem set S3_BUCKET in .env
   set AWS_PROFILE=etl
   python fetch_energinet.py 2026-10-20 2026-10-20
   python athena_checks.py 2026-10-20
   ```
3. **Airflow:** the official `docker-compose.yaml`, with this repo mounted into the containers
   (`PYTHONPATH=/opt/airflow/repo`), the `dags/` folder as the DAG folder, and the AWS config mounted read-only.

## The data and its quirks

| Quirk | What it does to a pipeline | How it is handled |
|---|---|---|
| Two time columns (`TimeUTC`, `TimeDK`) | A UTC day and a Danish day are different 24 hours | Files and partitions are by **Danish** date (`TimeDK`) |
| Daylight-saving days | A day has 23 or 25 hours: 184 or 200 rows instead of 192 | The Athena check accepts 184, 192 and 200 |
| Old dataset discontinued | `Elspotprices` (hourly) stopped updating on 30 Sep 2025 | Switched to `DayAheadPrices` (15-minute, from 1 Oct 2025) |
| API rate limits (HTTP 429) | Parallel backfill runs get rejected | Errors fail the task; Airflow retries after 30 minutes |
| Tomorrow's prices are published around 13:00 | An earlier run finds no data | The DAG runs at 14:00 and fails loudly on 0 rows |

## Design decisions

- **Raw is kept as received** (JSON Lines), clean is derived from it, so any day can be reprocessed.
- **Idempotent by design:** one file per Danish day with a fixed name; Glue overwrites only the partitions it
  processes. Re-running a day replaces it instead of duplicating it.
- **Fail loudly:** errors are logged and re-raised, so Airflow marks the task failed and retries.
- **Least privilege:** Airflow runs as an `etl` role that can only use this bucket, this Glue job,
  this catalog table and Athena; the Glue job has its own service role.
- **Glue is deliberately overkill** at ~200 rows a day: chosen to learn Spark and the Glue Data Catalog.
  At this volume, a Lambda or Glue Python shell job would be the cheaper choice.

## What broke along the way

- **A backfill hit Energinet's rate limit (429)** when three runs called the API at once.
  The task failed loudly and Airflow retried it, as designed. Bulk loads now run one at a time or as one ranged call.
- **Spark could not read JSON arrays** reliably, so the raw format was switched to JSON Lines and all days were reloaded.
- **The bucket was first created in the wrong region** (us-east-1) and recreated in eu-central-1, where the rest of the pipeline runs.
- **The crawler pointed one folder too high** and created a table `clean` with an extra `partition_0` column;
  it now points at the dataset folder.
- **The first version of the Athena check passed on a missing day:** with no rows, there were no "bad" rows either.
  It now also checks that the day exists, and a test against a day without data proves it fails.

## Operating it

![Duration of the last 10 DAG runs](docs/images/airflow-run-durations.png)

A normal daily run takes about 1–2 minutes end to end, most of it Glue starting up.

The 22 minute run was a backfill run of all the data available on this API.

## Next steps

- dbt models on Athena (staging + monthly price mart)
- Second dataset: CO2 emissions (`CO2Emis`), with the extractor taking the dataset as a parameter
- Range-aware checks (detect missing days), and the Glue job registering its own partitions
- Tests with pytest and GitHub Actions
- Warehouse layer: Redshift or Microsoft Fabric
