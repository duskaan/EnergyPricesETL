resource "aws_s3_bucket_public_access_block" "data" {
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = aws_s3_bucket.data.id
  ignore_public_acls      = true
  restrict_public_buckets = true
  skip_destroy            = null
}

resource "aws_s3_bucket" "data" {
  bucket = var.bucket_name
  lifecycle {
    prevent_destroy = true
  }
}

