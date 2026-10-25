resource "aws_s3_bucket_public_access_block" "data" {
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = var.bucket_name
  ignore_public_acls      = true
  region                  = "eu-central-1"
  restrict_public_buckets = true
  skip_destroy            = null
}

resource "aws_s3_bucket" "data" {
  bucket              = var.bucket_name
  bucket_namespace    = "global"
  force_destroy       = false
  object_lock_enabled = false
  region              = "eu-central-1"
  lifecycle {
    prevent_destroy = true
  }
}

