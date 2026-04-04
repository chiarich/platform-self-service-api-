# ---------------------------
# IAM Role for Lambda
# ---------------------------
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-${var.environment}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Basic Lambda logging policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ---------------------------
# DynamoDB Table
# ---------------------------
resource "aws_dynamodb_table" "buckets" {
  name         = "${var.project_name}-${var.environment}-buckets"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ---------------------------
# SNS Topic for Alerts
# ---------------------------
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
}

# Optional email alerts
# Replace with your real email if you want alerts
# resource "aws_sns_topic_subscription" "email_alerts" {
#   topic_arn = aws_sns_topic.alerts.arn
#   protocol  = "email"
#   endpoint  = "your-email@example.com"
# }

# ---------------------------
# Custom policy for S3 + DynamoDB
# ---------------------------
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.project_name}-${var.environment}-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3BucketProvisioning"
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:PutBucketTagging",
          "s3:HeadBucket",
          "s3:GetBucketLocation"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowDynamoDBAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.buckets.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# ---------------------------
# Lambda Function
# ---------------------------
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "main.handler"
  runtime       = "python3.11"

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  timeout = 12

  environment {
    variables = {
      ENVIRONMENT = var.environment
      TABLE_NAME  = aws_dynamodb_table.buckets.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_policy_attach
  ]
}

# ---------------------------
# API Gateway
# ---------------------------
resource "aws_apigatewayv2_api" "api" {
  name          = "${var.project_name}-${var.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.api.id

  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "root" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "Chiarich.sa@gmail.com"
}

# Allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

# ---------------------------
# CloudWatch Alarms
# ---------------------------
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-lambda-errors"
  alarm_description   = "Alarm when Lambda errors are greater than or equal to 1"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.project_name}-${var.environment}-lambda-duration"
  alarm_description   = "Alarm when Lambda average duration is too high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 8000
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Average"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.api.function_name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# ---------------------------
# Outputs
# ---------------------------
output "api_url" {
  value = aws_apigatewayv2_api.api.api_endpoint
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.buckets.name
}

output "lambda_function_name" {
  value = aws_lambda_function.api.function_name
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}