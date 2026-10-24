import {
  to = aws_s3_bucket.data
  id = "energyprices-etl-tim-v1"
}

import {
  to = aws_s3_bucket_public_access_block.data
  id = "energyprices-etl-tim-v1"
}

import {
  to = aws_glue_job.clean_dayaheadprices
  id = "clean_dayaheadprices"
}

import {
  to = aws_s3_object.glue_script
  id = "aws-glue-assets-407525820051-eu-central-1/scripts/clean_dayaheadprices.py"
}