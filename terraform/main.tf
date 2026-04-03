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

# Custom policy for S3 + DynamoDB
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.project_name}-${var.environment}-lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:PutBucketTagging",
          "s3:GetObject",
          "s3:PutObject",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
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
# Lambda Function
# ---------------------------
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "main.handler"
  runtime       = "python3.11"

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  timeout = 10

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      TABLE_NAME    = aws_dynamodb_table.buckets.name
    }
  }
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

resource "aws_apigatewayv2_route" "any" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "ANY /{proxy+}"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

# Allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
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