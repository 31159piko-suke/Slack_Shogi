# --------------------
# Lambda IAM Policy
# --------------------
resource "aws_iam_policy" "lambda_basic_execution" {
  name = "${var.project}_LambdaBasicExecution"
  policy = templatefile("iam_policy_documents/LambdaBasicExecutionPolicy.json", {
    account_id = var.account_id
    region     = var.region
  })
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
    function_name = "SlackShogiAction"
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
  runtime       = "python3.9"

  filename         = data.archive_file.lambda_slack_shogi_action.output_path
  source_code_hash = data.archive_file.lambda_slack_shogi_action.output_base64sha256

  timeout = 180

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
