# --------------------
# Lambda IAM Policy
# --------------------
resource "aws_iam_policy" "lambda_basic_execution" {
  name   = "${var.project}_LambdaBasicExecution"
  policy = file("iam_policy_documents/LambdaBasicExecutionPolicy.json")
  tags = {
    Project  = var.project,
    Resource = "iam_policy"
  }
}

resource "aws_iam_policy" "lambda_invoke_function" {
  name = "${var.project}_LambdaInvokeFunction"
  policy = templatefile("iam_policy_documents/LambdaInvokeFunctionPolicy.json", {
    account_id    = var.account_id
    region        = var.region,
    function_name = "Slack_Shogi_Action"
  })
  tags = {
    Project  = var.project,
    Resource = "iam_policy"
  }
}

# --------------------
# Lambda IAM Role
# --------------------
resource "aws_iam_role" "lambda_slack_shogi_action" {
  name               = "${var.project}_SlackShogiAction"
  assume_role_policy = file("iam_policy_documents/LambdaAssumeRolePolicy.json")
  managed_policy_arns = [
    aws_iam_policy.dynamo_put.arn,
    aws_iam_policy.s3_put.arn,
    aws_iam_policy.lambda_basic_execution.arn,
    aws_iam_policy.lambda_invoke_function.arn,
  ]
  tags = {
    Project  = var.project,
    Resource = "iam_role"
  }
}

# --------------------
# Lambda
# --------------------
data "archive_file" "lambda_slack_shogi_action" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/Shogi"
  output_path = "${path.module}/archive/lambda_shogi.zip"
}

resource "aws_lambda_function" "slack_shogi_action" {
  function_name = "${var.project}_Action"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda_slack_shogi_action.arn
  runtime       = "python3.8"
  layers = ["arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-python38-numpy:25",
    "arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-python38-matplotlib:46",
    "arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-python38-requests:28",
    "arn:aws:lambda:ap-northeast-1:00${var.account_id}:layer:slack-bolt:1",
  "arn:aws:lambda:ap-northeast-1:00${var.account_id}:layer:pillow:2"]
  environment {
    variables = {
      SLACK_SIGNING_SECRET              = var.SLACK_SIGNING_SECRET
      SLACK_CLIENT_ID                   = var.SLACK_CLIENT_ID
      SLACK_CLIENT_SECRET               = var.SLACK_CLIENT_SECRET
      SLACK_SCOPES                      = var.SLACK_SCOPES
      SLACK_INSTALLATION_S3_BUCKET_NAME = var.SLACK_INSTALLATION_S3_BUCKET_NAME
      SLACK_STATE_S3_BUCKET_NAME        = var.SLACK_STATE_S3_BUCKET_NAME
      MPLCONFIGDIR                      = var.MPLCONFIGDIR

    }
  }
  memory_size      = 512
  timeout          = 180
  filename         = data.archive_file.lambda_slack_shogi_action.output_path
  source_code_hash = data.archive_file.lambda_slack_shogi_action.output_base64sha256
  tags = {
    Project  = var.project,
    Resource = "lambda"
  }
}

resource "aws_lambda_permission" "apigw_slack_shogi_action" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_shogi_action.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.slack_shogi_api.execution_arn}/*/*"
}
