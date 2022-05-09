# --------------------
# DynamoDB
# --------------------
resource "aws_dynamodb_table" "user_manage" {
  name         = "${var.project}_UserManage"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UserID"

  attribute {
    name = "UserID"
    type = "S"
  }

  tags = {
    Project  = var.project,
    Resource = "dynamodb"
  }
}

# --------------------
# DynamoDB IAM Policy
# --------------------
resource "aws_iam_policy" "dynamo_put" {
  name = "${var.project}_DynamoDBPut"
  policy = templatefile("iam_policy_documents/DynamoDBPutPolicy.json", {
    account_id = var.account_id
    region     = var.region
    table_name = aws_dynamodb_table.user_manage.name
  })
  tags = {
    Project  = var.project,
    Resource = "iam_policy"
  }
}


