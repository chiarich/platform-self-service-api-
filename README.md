Platform Self-Service API

This project is a cloud-native self-service platform API that allows development teams to request and provision standardized S3 buckets through a REST interface.

It demonstrates end-to-end platform engineering using AWS, serverless architecture, and infrastructure as code.

🚀 Features
Create S3 buckets via API
Store request metadata in DynamoDB
Serverless backend using AWS Lambda
REST API powered by FastAPI
Infrastructure managed with Terraform
API exposed through API Gateway
Input validation using Pydantic
🏗️ Architecture
Client → API Gateway → Lambda (FastAPI) → S3 + DynamoDB
Flow:
Client sends a POST request to /buckets
API validates input
Lambda:
Creates an S3 bucket
Stores request in DynamoDB
Response returned with request details
🧰 Tech Stack
Python / FastAPI
AWS Lambda
Amazon API Gateway
Amazon S3
Amazon DynamoDB
Terraform
Boto3
Mangum (ASGI adapter)
📦 API Endpoints
Health Check
GET /
Create Bucket
POST /buckets
Request Body:
{
  "team_name": "platform-team",
  "environment": "dev",
  "bucket_name": "platform-team-dev-demo",
  "purpose": "testing s3 creation"
}
Response:
{
  "request_id": "uuid",
  "status": "created",
  "message": "Bucket created successfully",
  "bucket_name": "platform-team-dev-demo",
  "team_name": "platform-team",
  "environment": "dev"
}
Get All Buckets
GET /buckets
Get Single Bucket
GET /buckets/{bucket_id}
Update Bucket
PUT /buckets/{bucket_id}
Delete Bucket
DELETE /buckets/{bucket_id}
⚙️ Infrastructure (Terraform)

Resources provisioned:

Lambda Function
API Gateway (HTTP API)
DynamoDB Table (platform-api-dev-buckets)
IAM Roles & Policies

To deploy:

cd terraform
terraform init
terraform plan
terraform apply
🧪 Local Development

Start FastAPI locally:

uvicorn app.main:app --reload

Access:

Swagger UI → http://127.0.0.1:8000/docs
ReDoc → http://127.0.0.1:8000/redoc
☁️ Deployment (Lambda)

Build and deploy:

pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.11 --only-binary=:all: --target build fastapi mangum pydantic
Copy-Item -Recurse app build\app
Copy-Item app\main.py build\main.py
Compress-Archive -Path build\* -DestinationPath dist\lambda.zip -Force

aws lambda update-function-code --function-name platform-api-dev --zip-file fileb://dist/lambda.zip
🔐 IAM Permissions

Lambda is configured with permissions for:

s3:CreateBucket
s3:PutObject
dynamodb:PutItem
dynamodb:GetItem
dynamodb:Scan
📌 Current Status
✅ End-to-end working API
✅ S3 bucket provisioning
✅ DynamoDB persistence
✅ Serverless deployment via Terraform
🔄 Future improvements:
Input sanitization enhancements
Bucket naming policies
Monitoring & alerts (CloudWatch)
CI/CD pipeline (GitHub Actions)
🎯 Project Purpose

This project demonstrates:

Platform engineering principles
Infrastructure as Code (IaC)
Serverless application design
API-driven resource provisioning
AWS cloud integration
👤 Author

Richard Chia Ndum

⭐ Notes

This project simulates a real-world internal platform where teams can self-service infrastructure requests without direct cloud access.