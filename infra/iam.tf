resource "aws_iam_role_policy_attachment" "glue_service" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
  role       = "GlueRole"
}

# "GlueRole:AWSGlueConsoleRoleInlinePolicy-read-and-write-specific-access-1792439405213"
resource "aws_iam_role_policy" "glue_s3" {
  name = "AWSGlueConsoleRoleInlinePolicy-read-and-write-specific-access-1792439405213"
  policy = jsonencode({
    Statement = [{
      Action   = ["s3:GetObject", "s3:ListBucket", "s3:PutObject","s3:DeleteObject"]
      Effect   = "Allow"
      Resource = ["arn:aws:s3:::energyprices-etl-tim-v1/*", "arn:aws:s3:::energyprices-etl-tim-v1"]
    }]
    Version = "2012-10-17"
  })
  role = "GlueRole"
}

# "GlueRole"
resource "aws_iam_role" "glue" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
  description           = "Allows S3 to call AWS services on your behalf."
  force_detach_policies = false
  max_session_duration  = 3600
  name                  = "GlueRole"
  path                  = "/"
  permissions_boundary  = null
  tags                  = {}
  tags_all              = {}
}


# "etl"
resource "aws_iam_role" "etl" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action    = "sts:AssumeRole"
      Condition = {}
      Effect    = "Allow"
      Principal = {
        AWS = "arn:aws:iam::407525820051:user/Tim_DEV"
      }
    }]
    Version = "2012-10-17"
  })
  description           = null
  force_detach_policies = false
  max_session_duration  = 3600
  name                  = "etl"
  path                  = "/"
  permissions_boundary  = null
  tags                  = {}
  tags_all              = {}
}
