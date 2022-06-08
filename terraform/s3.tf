# --------------------
# S3
# --------------------
resource "aws_s3_bucket" "slack_shogi" {
  bucket = "slack-shogi"
  tags = {
    Project  = var.project,
    Resource = "s3"
  }
}

resource "aws_s3_bucket_acl" "slack_shogi" {
  bucket = aws_s3_bucket.slack_shogi.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "slack_shogi" {
  bucket = aws_s3_bucket.slack_shogi.id
  rule {
    id     = "rule1"
    status = "Enabled"

    expiration {
      days = 1
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "slack_shogi" {
  bucket = aws_s3_bucket.slack_shogi.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "slack_shogi" {
  bucket                  = aws_s3_bucket.slack_shogi.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "slack_shogi_installation" {
  bucket = "slack-shogi-installation"
  tags = {
    Project  = var.project,
    Resource = "s3"
  }
}

resource "aws_s3_bucket_acl" "slack_shogi_installation" {
  bucket = aws_s3_bucket.slack_shogi_installation.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "slack_shogi_installation" {
  bucket = aws_s3_bucket.slack_shogi_installation.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "slack_shogi_installation" {
  bucket                  = aws_s3_bucket.slack_shogi_installation.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "slack_shogi_state" {
  bucket = "slack-shogi-state"
  tags = {
    Project  = var.project,
    Resource = "s3"
  }
}

resource "aws_s3_bucket_acl" "slack_shogi_state" {
  bucket = aws_s3_bucket.slack_shogi_state.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "slack_shogi_state" {
  bucket = aws_s3_bucket.slack_shogi_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "slack_shogi_state" {
  bucket                  = aws_s3_bucket.slack_shogi_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# --------------------
# S3 IAM Policy
# --------------------
resource "aws_iam_policy" "s3_put" {
  name = "${var.project}_S3Put"
  policy = templatefile("iam_policy_documents/S3PutPolicy.json", {
    bucket_name         = aws_s3_bucket.slack_shogi.bucket
    bucket_installation = aws_s3_bucket.slack_shogi_installation.bucket
    bucket_state        = aws_s3_bucket.slack_shogi_state.bucket
  })
  tags = {
    Project  = var.project,
    Resource = "iam_policy"
  }
}
