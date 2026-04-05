🧠 Platform Self-Service API

This project is a cloud-native Internal Developer Platform (IDP) that enables development teams to self-service S3 bucket provisioning through a REST API.

It demonstrates end-to-end platform engineering using AWS, serverless architecture, infrastructure as code, CI/CD, and AI-assisted development.

🎯 Project Goal

Build a platform service that allows teams to:

Request infrastructure via API
Automatically provision resources (S3)
Track requests in a data store (DynamoDB)
Operate with observability and automation

🚀 Features
Create S3 buckets via API
Store request metadata in DynamoDB
Serverless backend using AWS Lambda
REST API powered by FastAPI
Infrastructure managed with Terraform
API exposed through API Gateway
Input validation using Pydantic
Duplicate bucket protection
CloudWatch logging and alerts

🏗️ Architecture


[Client]
     ↓
[API Gateway]
     ↓
[Lambda (FastAPI)]
     ↓
 ┌───────────────┬───────────────┐
 ↓               ↓               ↓
[S3 Bucket]   [DynamoDB Table]    SNS


Flow
Client sends a POST request to /buckets
API validates input
Lambda:
Generates bucket name
Checks for duplicates
Creates S3 bucket
Stores metadata in DynamoDB
Response returned with request details
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
  "purpose": "testing s3 creation"
}
Behavior
Bucket name is generated as:
platform-<team>-<environment>-<unique_suffix>
Duplicate requests return:
{
  "detail": "Bucket '<name>' already exists"
}
Other Endpoints
GET /buckets
GET /buckets/{bucket_id}
PUT /buckets/{bucket_id}
DELETE /buckets/{bucket_id}
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
Builds Lambda deployment package
Deploys infrastructure and application

Pipeline file:

.github/workflows/deploy.yml
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
CloudWatch alarms:
Lambda errors
Lambda duration
SNS topic for alert notifications
🔐 IAM Permissions

Lambda is configured with:

s3:CreateBucket
s3:PutBucketTagging
s3:HeadBucket
dynamodb:PutItem
dynamodb:GetItem
dynamodb:Scan
Least Privilege Approach
DynamoDB access is scoped to the specific table ARN
Lambda logging uses AWS managed policy:
AWSLambdaBasicExecutionRole
S3 permissions remain broader due to dynamic bucket creation

See DECISIONS.md for detailed tradeoff explanation.

🧪 Demo Flow
Send POST request to /buckets
Bucket is created
Metadata stored in DynamoDB
Send same request again
Duplicate error returned
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
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --target build fastapi mangum pydantic
Copy-Item -Recurse app build\app
Copy-Item app\main.py build\main.py
Compress-Archive -Path build\* -DestinationPath dist\lambda.zip -Force

aws lambda update-function-code --function-name <function-name> --zip-file fileb://dist/lambda.zip

📌 Current Status
End-to-end working platform API
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