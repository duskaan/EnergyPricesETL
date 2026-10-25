resource "aws_s3_object" "glue_etl_script" {
  bucket = "aws-glue-assets-407525820051-eu-central-1"
  key    = "scripts/clean_dayaheadprices.py"
  source = "${path.module}/../glue/clean_dayaheadprices.py"
  etag   = filemd5("${path.module}/../glue/clean_dayaheadprices.py")
}

resource "aws_glue_job" "clean_dayaheadprices" {
  default_arguments = {
    "--TempDir"                          = "s3://aws-glue-assets-407525820051-eu-central-1/temporary/"
    "--conf"                             = "spark.eventLog.rolling.enabled=true --conf spark.sql.catalog.glue_catalog.glue.skip-name-validation=true"
    "--date"                             = "ALL"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-glue-datacatalog"          = ""
    "--enable-job-insights"              = "true"
    "--enable-metrics"                   = ""
    "--enable-observability-metrics"     = "true"
    "--enable-spark-ui"                  = "true"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--job-language"                     = "python"
    "--spark-event-logs-path"            = "s3://aws-glue-assets-407525820051-eu-central-1/sparkHistoryLogs/"
  }
  description             = "This job is set to clean the data from the raw energyprices a day ahead to a clean version back in s3"
  execution_class         = "STANDARD"
  glue_version            = "5.1"
  job_mode                = "SCRIPT"
  job_run_queuing_enabled = false
  max_retries             = 0
  name                    = "clean_dayaheadprices"
  number_of_workers       = 2
  role_arn                = aws_iam_role.glue.arn
  timeout                 = 10
  worker_type             = "G.1X"
  command {
    name            = "glueetl"
    python_version  = "3"
    script_location = "s3://${aws_s3_object.glue_etl_script.bucket}/${aws_s3_object.glue_etl_script.key}"
  }
  execution_property {
    max_concurrent_runs = 1
  }
}
