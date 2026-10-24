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
  to = aws_s3_object.glue_etl_script
  id = "aws-glue-assets-407525820051-eu-central-1/scripts/clean_dayaheadprices.py"
}

import {
  to = aws_iam_role.glue
  id = "GlueRole"
}

import {
  to = aws_iam_role.etl
  id = "etl"
}


import {
  to = aws_iam_role_policy_attachment.glue_service
  id = "GlueRole/arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

import {
  to = aws_iam_role_policy.glue_s3
  id = "GlueRole:AWSGlueConsoleRoleInlinePolicy-read-and-write-specific-access-1792439405213"
}
