resource "aws_s3_bucket_public_access_block" "data" {
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = "energyprices-etl-tim-v1"
  ignore_public_acls      = true
  region                  = "eu-central-1"
  restrict_public_buckets = true
  skip_destroy            = null
}

# __generated__ by Terraform from "energyprices-etl-tim-v1"
resource "aws_s3_bucket" "data" {
  bucket              = "energyprices-etl-tim-v1"
  bucket_namespace    = "global"
  force_destroy       = false
  object_lock_enabled = false
  region              = "eu-central-1"
  tags                = {}
  tags_all            = {}
  lifecycle {
    prevent_destroy = true
  }
}

