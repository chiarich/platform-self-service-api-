
## `terraform/outputs.tf`

```hcl
# ---------------------------
# Outputs
# ---------------------------

output "api_url" {
  description = "Base API Gateway URL"
  value       = aws_apigatewayv2_api.api.api_endpoint
}

output "create_bucket_url" {
  description = "Endpoint for creating S3 buckets"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/buckets"
}

output "buckets_url" {
  description = "Endpoint for listing S3 bucket requests"
  value       = "${aws_apigatewayv2_api.api.api_endpoint}/buckets"
}

output "dynamodb_table_name" {
  description = "DynamoDB table storing bucket requests"
  value       = aws_dynamodb_table.buckets.name
}

output "lambda_function_name" {
  description = "Deployed Lambda function name"
  value       = aws_lambda_function.api.function_name
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}