# ---------------------------
# Project Configuration
# ---------------------------
variable "project_name" {
  description = "Name of the project (used for resource naming)"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g. dev, prod)"
  type        = string
}

# ---------------------------
# Lambda Configuration
# ---------------------------
variable "lambda_zip_path" {
  description = "Path to the Lambda deployment package zip file"
  type        = string
}

# ---------------------------
# Alerting Configuration
# ---------------------------
variable "alert_email" {
  description = "Email address to receive SNS alerts"
  type        = string
}

# ---------------------------
# Logging / Observability
# ---------------------------
variable "log_retention_in_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 14
}

# ---------------------------
# Optional Enhancements
# ---------------------------
variable "bucket_name_prefix" {
  description = "Prefix for all S3 buckets created by the application"
  type        = string
  default     = ""
}

variable "enable_tags" {
  description = "Enable tagging for all resources"
  type        = bool
  default     = true
}

# ---------------------------
# AWS Region (Optional override)
# ---------------------------
variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}