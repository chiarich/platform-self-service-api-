README.md
🧠 Platform Self-Service API

This project is a cloud-native Internal Developer Platform (IDP) that enables development teams to self-service S3 bucket provisioning through a REST API.

It demonstrates end-to-end platform engineering using AWS, serverless architecture, infrastructure as code, CI/CD, and AI-assisted development.

## 🎯 Project Goal

Build a platform service that allows teams to:

- Request infrastructure via API
- Provision S3 buckets through a platform workflow
- Track requests in a data store (DynamoDB)
- Operate with observability and automation

## 🚀 Features

- Create S3 buckets via API
- Store request metadata in DynamoDB
- Serverless backend using AWS Lambda
- REST API powered by FastAPI
- Infrastructure managed with Terraform
- API exposed through API Gateway
- Input validation using Pydantic
- Duplicate bucket protection
- CloudWatch logging and alerts

## 🏗️ Architecture

```text
[Client]
     ↓
[API Gateway]
     ↓
[Lambda (FastAPI via Mangum)]
     ↓
 ┌───────────────┬───────────────┐
 ↓               ↓               ↓
[S3 Bucket]   [DynamoDB Table]    SNS
Flow
Client sends a POST request to /buckets
API validates input
Lambda:
validates the user-provided bucket_name
checks for duplicates
creates the S3 bucket
stores metadata in DynamoDB
Response is returned with request details

🧰 Tech Stack
Python / FastAPI
AWS Lambda
Amazon API Gateway (HTTP API)
Amazon S3
Amazon DynamoDB
Terraform
Boto3
Mangum (ASGI adapter)
GitHub Actions (CI/CD)

📦 API Endpoints
Health Check

GET /

Create Bucket

POST /buckets

Request Body
{
  "team_name": "platform-team",
  "environment": "dev",
  "bucket_name": "platform-test-bucket-for-rich",
  "purpose": "testing s3 creation"
}
Behavior
Client must provide a globally unique bucket_name
Duplicate requests return an error such as:
{
  "detail": "Bucket '<name>' already exists"
}
Other Endpoints
GET /buckets
GET /buckets/{bucket_id}
PUT /buckets/{bucket_id}
DELETE /buckets/{bucket_id}

⚠️ API Design Note

{bucket_id} refers to the internal request record ID stored in DynamoDB, not the S3 bucket name.

To retrieve or delete a specific request:

Call GET /buckets
Copy the returned id
Use that id in GET /buckets/{bucket_id} or DELETE /buckets/{bucket_id}

This reflects a common platform API pattern where tracking records are distinct from cloud resource names.

⚙️ Infrastructure (Terraform)

Resources provisioned:

Lambda Function
API Gateway (HTTP API)
DynamoDB Table
IAM Roles & Policies
CloudWatch Alarms
SNS Topic
Deploy
cd terraform
terraform init
terraform plan
terraform apply

🚀 CI/CD (GitHub Actions)

The project includes a CI/CD pipeline that:

Runs Terraform checks:
terraform fmt
terraform validate
terraform plan
Builds the Lambda deployment package
Deploys infrastructure and application
Captures Terraform outputs
Publishes an API usage guide artifact
Adds a deployment summary with the live API endpoints

Pipeline file:

.github/workflows/deploy.yml
Quick Demo
Base API URL

After deployment, Terraform outputs the base API URL.

Create Bucket Endpoint

The pipeline also publishes the exact create-bucket endpoint:

https://<api-id>.execute-api.us-east-1.amazonaws.com/buckets
Example curl
curl -X POST "https://<api-id>.execute-api.us-east-1.amazonaws.com/buckets" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "platform-team",
    "environment": "dev",
    "bucket_name": "platform-test-bucket-for-rich",
    "purpose": "demo bucket creation"
  }'
Example PowerShell
$body = @{
  team_name   = "platform-team"
  environment = "dev"
  bucket_name = "platform-test-bucket-for-rich"
  purpose     = "demo bucket creation"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://<api-id>.execute-api.us-east-1.amazonaws.com/buckets" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

🤖 AI-Native Development Workflow

AI (ChatGPT) was used as a development collaborator for:

Architecture design
Terraform generation
Debugging Lambda packaging issues
CI/CD pipeline creation
IAM policy refinement

AI workflow is documented in:

CHATGPT.md

AI outputs were always:

reviewed
validated
corrected where necessary

📊 Observability
CloudWatch logs enabled for Lambda
CloudWatch alarms for:
Lambda errors
Lambda duration
SNS topic for alert notifications

🔐 IAM Permissions

Lambda is configured with:

s3:CreateBucket
s3:PutBucketTagging
s3:HeadBucket
s3:GetBucketLocation
dynamodb:PutItem
dynamodb:GetItem
dynamodb:Scan
Least Privilege Approach
DynamoDB access is scoped to the specific table ARN
Lambda logging uses the AWS managed policy:
AWSLambdaBasicExecutionRole
S3 permissions remain broader due to dynamic bucket creation requirements

See DECISIONS.md for detailed tradeoff explanation.

🧪 Demo Flow
Send POST /buckets
Bucket is created
Metadata is stored in DynamoDB
Send same request again
Duplicate error is returned

Verify:

S3 bucket exists
DynamoDB record exists
CloudWatch logs show activity

📄 Assignment Requirement Mapping
AI-Native Development Workflow
ChatGPT used as development collaborator
AI workflow documented in CHATGPT.md
Demonstrates iterative development and validation
Terraform & CI/CD
Infrastructure fully defined in Terraform
CI/CD pipeline implemented with GitHub Actions
Automation Service
Self-service API for S3 provisioning
Input validation and error handling included
DynamoDB used as data store
Observability
Logging via CloudWatch
Alerts via CloudWatch + SNS
Documentation
README (this file)
DECISIONS.md
CHATGPT.md
Architecture diagrams

🧪 Local Development
uvicorn app.main:app --reload

Access:

Swagger UI → http://127.0.0.1:8000/docs
ReDoc → http://127.0.0.1:8000/redoc

☁️ Lambda Deployment
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --target build fastapi mangum pydantic boto3

PowerShell packaging example:

Copy-Item -Recurse app build\app
Copy-Item app\main.py build\main.py
Compress-Archive -Path build\* -DestinationPath dist\lambda.zip -Force
aws lambda update-function-code --function-name <function-name> --zip-file fileb://dist/lambda.zip

📌 Current Status
End-to-end working platform API locally
Infrastructure deployed via Terraform
Observability implemented
CI/CD pipeline configured
AI workflow documented
Demo-ready

🔄 Future Improvements
Replace AWS credentials with GitHub OIDC
Further tighten IAM permissions using permission boundaries
Modularize Terraform into reusable modules
Add automated tests in CI pipeline
Add API authentication (API Gateway authorizer or IAM auth)
Add CloudWatch dashboards
Add lookup by bucket name for improved usability

🎯 Project Purpose

This project demonstrates:

Platform engineering principles
Infrastructure as Code (IaC)
Serverless application design
API-driven infrastructure provisioning
Observability and operational awareness
AI-assisted development workflows

👤 Author

Richard Chia Ndum

⭐ Notes

This project simulates a real-world internal platform where development teams can self-service infrastructure safely and efficiently without direct access to cloud resources.


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
.github/workflows/deploy.yml
name: Deploy Platform Self-Service API

on:
  push:
    branches:
      - main
      - improve/ai-workflow-and-security
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs:
  terraform-and-deploy:
    runs-on: ubuntu-latest

    env:
      AWS_REGION: us-east-1
      TF_WORKING_DIR: terraform

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Install Python dependencies for Lambda package
        run: |
          python -m pip install --upgrade pip
          rm -rf build dist
          mkdir -p build dist
          pip install \
            --platform manylinux2014_x86_64 \
            --implementation cp \
            --python-version 3.11 \
            --only-binary=:all: \
            --target build \
            fastapi mangum pydantic boto3

      - name: Copy application files
        run: |
          mkdir -p build/app
          cp -r app/* build/app/
          cp app/main.py build/main.py

      - name: Create Lambda deployment package
        run: |
          cd build
          zip -r ../dist/lambda.zip .

      - name: Terraform fmt check
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: terraform fmt -check

      - name: Terraform init
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: |
          terraform init \
            -backend-config="bucket=platform-api-terraform-state-richard-1" \
            -backend-config="key=platform-self-service-api/dev/terraform.tfstate" \
            -backend-config="region=us-east-1"

      - name: Terraform validate
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: terraform validate

      - name: Import existing Lambda if already created
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: |
          if aws lambda get-function --function-name platform-api-dev > /dev/null 2>&1; then
            echo "Lambda already exists in AWS."

            if ! terraform state list | grep -q "aws_lambda_function.api"; then
              echo "Importing existing Lambda into Terraform state..."
              terraform import aws_lambda_function.api platform-api-dev || true
            else
              echo "Lambda already exists in Terraform state."
            fi
          else
            echo "Lambda does not exist yet."
          fi

      - name: Terraform plan
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: terraform plan -input=false -var="lambda_zip_path=../dist/lambda.zip"

      - name: Terraform apply
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        working-directory: ${{ env.TF_WORKING_DIR }}
        run: terraform apply -auto-approve -input=false -var="lambda_zip_path=../dist/lambda.zip"

      - name: Capture Terraform outputs
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        working-directory: ${{ env.TF_WORKING_DIR }}
        shell: bash
        run: |
          set -euo pipefail

          API_URL="$(terraform output -raw api_url)"
          CREATE_BUCKET_URL="$(terraform output -raw create_bucket_url)"
          BUCKETS_URL="$(terraform output -raw buckets_url)"
          DYNAMODB_TABLE_NAME="$(terraform output -raw dynamodb_table_name)"
          LAMBDA_FUNCTION_NAME="$(terraform output -raw lambda_function_name)"
          SNS_TOPIC_ARN="$(terraform output -raw sns_topic_arn)"

          echo "API_URL=$API_URL" >> "$GITHUB_ENV"
          echo "CREATE_BUCKET_URL=$CREATE_BUCKET_URL" >> "$GITHUB_ENV"
          echo "BUCKETS_URL=$BUCKETS_URL" >> "$GITHUB_ENV"
          echo "DYNAMODB_TABLE_NAME=$DYNAMODB_TABLE_NAME" >> "$GITHUB_ENV"
          echo "LAMBDA_FUNCTION_NAME=$LAMBDA_FUNCTION_NAME" >> "$GITHUB_ENV"
          echo "SNS_TOPIC_ARN=$SNS_TOPIC_ARN" >> "$GITHUB_ENV"

          echo "Base API URL: $API_URL"
          echo "Create Bucket URL: $CREATE_BUCKET_URL"
          echo "Buckets URL: $BUCKETS_URL"
          echo "DynamoDB Table Name: $DYNAMODB_TABLE_NAME"
          echo "Lambda Function Name: $LAMBDA_FUNCTION_NAME"
          echo "SNS Topic ARN: $SNS_TOPIC_ARN"

      - name: Create API usage guide
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        shell: bash
        run: |
          mkdir -p release
          cat > release/api-usage-guide.txt <<EOF
          Platform Self-Service API - Usage Guide

          Base API URL:
          $API_URL

          Create Bucket Endpoint:
          $CREATE_BUCKET_URL

          Buckets Endpoint:
          $BUCKETS_URL

          DynamoDB Table Name:
          $DYNAMODB_TABLE_NAME

          Lambda Function Name:
          $LAMBDA_FUNCTION_NAME

          SNS Topic ARN:
          $SNS_TOPIC_ARN

          Available endpoints:
          GET  $API_URL/
          POST $CREATE_BUCKET_URL
          GET  $BUCKETS_URL
          GET  $BUCKETS_URL/{bucket_id}
          PUT  $BUCKETS_URL/{bucket_id}
          DELETE $BUCKETS_URL/{bucket_id}

          Example request body for creating a bucket:
          {
            "team_name": "platform-team",
            "environment": "dev",
            "bucket_name": "platform-test-bucket-for-rich",
            "purpose": "demo bucket creation"
          }

          Example curl command:
          curl -X POST $CREATE_BUCKET_URL \\
            -H "Content-Type: application/json" \\
            -d '{
              "team_name": "platform-team",
              "environment": "dev",
              "bucket_name": "platform-test-bucket-for-rich",
              "purpose": "demo bucket creation"
            }'

          Example PowerShell:
          \$body = @{
            team_name   = "platform-team"
            environment = "dev"
            bucket_name = "platform-test-bucket-for-rich"
            purpose     = "demo bucket creation"
          } | ConvertTo-Json

          Invoke-RestMethod \`
            -Uri "$CREATE_BUCKET_URL" \`
            -Method POST \`
            -ContentType "application/json" \`
            -Body \$body

          Notes:
          - bucket_name must be globally unique in S3 and should be lowercase.
          - {bucket_id} refers to the internal DynamoDB request record ID, not the bucket name.
          - To retrieve or delete a request, first call GET /buckets and copy the returned id.
          - If the bucket already exists, the API returns an error.
          - Request metadata is stored in DynamoDB.
          - Monitoring is handled through CloudWatch and SNS alerts.
          EOF

      - name: Upload API usage guide artifact
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: platform-api-usage-guide
          path: release/api-usage-guide.txt

      - name: Add deployment summary
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        shell: bash
        run: |
          {
            echo "## Deployment Complete"
            echo ""
            echo "**Base API URL:** $API_URL"
            echo ""
            echo "**Create Bucket URL:** $CREATE_BUCKET_URL"
            echo ""
            echo "**Buckets URL:** $BUCKETS_URL"
            echo ""
            echo "**DynamoDB Table Name:** $DYNAMODB_TABLE_NAME"
            echo ""
            echo "**Lambda Function Name:** $LAMBDA_FUNCTION_NAME"
            echo ""
            echo "**SNS Topic ARN:** $SNS_TOPIC_ARN"
            echo ""
            echo "### Example Create Bucket Request"
            echo "\`\`\`json"
            echo '{'
            echo '  "team_name": "platform-team",'
            echo '  "environment": "dev",'
            echo '  "bucket_name": "platform-test-bucket-for-rich",'
            echo '  "purpose": "demo bucket creation"'
            echo '}'
            echo "\`\`\`"
            echo ""
            echo "### Notes"
            echo "- bucket_name must be globally unique and lowercase."
            echo "- {bucket_id} is the internal DynamoDB request record ID."
            echo "- Use GET /buckets first to retrieve the correct id for GET/DELETE by id."
            echo ""
            echo "The downloadable artifact contains usage instructions."
          } >> "$GITHUB_STEP_SUMMARY"