# --------------------
# APIGW  Setting
# --------------------
# resource "aws_iam_role" "cloudwatch" {
#   name               = "${var.project}_APIGatewayCloudwatchGlobal"
#   assume_role_policy = file("iam_policy_documents/APIGatewayCloudwatchGlobal.json")

#   tags = {
#     Project  = var.project,
#     Resource = "apigateway"
#   }
# }

# resource "aws_iam_role_policy" "cloudwatch" {
#   name = "default"
#   role = aws_iam_role.cloudwatch.id
#   policy = templatefile("iam_policy_documents/APIGatewayCloudwatchPolicy.json", {
#     account_id = var.account_id
#     region     = var.region
#   })
# }

# resource "aws_api_gateway_account" "account" {
#   cloudwatch_role_arn = aws_iam_role.cloudwatch.arn
#   depends_on          = [aws_iam_role.cloudwatch]
# }


# --------------------
# API Gateway
# --------------------
data "template_file" "swagger" {
  template = file("${path.module}/swagger.yaml")
  vars = {
    lambda_slack_shogi_action = aws_lambda_function.slack_shogi_action.invoke_arn,

  }
}

resource "aws_api_gateway_rest_api" "slack_shogi_api" {
  name = "${var.project}API"
  body = data.template_file.swagger.rendered

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Project  = var.project,
    Resource = "apigateway"
  }
}

resource "aws_api_gateway_deployment" "default" {
  rest_api_id = aws_api_gateway_rest_api.slack_shogi_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.slack_shogi_api.body
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.slack_shogi_api.id
  deployment_id = aws_api_gateway_deployment.default.id
}

# resource "aws_api_gateway_method_settings" "slack_shogi_api" {
#   rest_api_id = aws_api_gateway_rest_api.slack_shogi_api.id
#   stage_name  = aws_api_gateway_stage.dev.stage_name
#   method_path = "*/*"

#   settings {
#     logging_level      = "ERROR"
#     data_trace_enabled = true
#     metrics_enabled    = true
#   }

# depends_on = [
#   aws_api_gateway_account.account
# ]
# }
