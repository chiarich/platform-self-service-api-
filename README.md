# 🧠 Platform Self-Service API

This project is a cloud-native Internal Developer Platform (IDP) that enables development teams to self-service S3 bucket provisioning through a REST API.

It demonstrates end-to-end platform engineering using AWS, serverless architecture, infrastructure as code, CI/CD, observability, and an AI-assisted development workflow.

## Challenge Alignment

This project addresses the platform engineering challenge by delivering a self-service API for S3 bucket lifecycle management, implemented with Terraform-managed infrastructure, CI/CD automation, observability, and a documented AI-assisted development workflow.

---

## 🎯 Project Goal

Build a platform service that allows teams to:

* Request infrastructure via API
* Provision S3 buckets through a platform workflow
* Track requests in a data store (DynamoDB)
* Operate with observability and automation

---

## 🚀 Features

* Create S3 buckets via API
* Store request metadata in DynamoDB
* Serverless backend using AWS Lambda
* REST API powered by FastAPI
* Infrastructure managed with Terraform
* API exposed through API Gateway
* Input validation using Pydantic
* Duplicate bucket protection
* CloudWatch logging and alerts
* CI/CD pipeline with deployment summaries and artifacts

---

## 🏗️ Architecture

```
[Client]
     ↓
[API Gateway]
     ↓
[Lambda (FastAPI via Mangum)]
     ↓
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓
[S3 Bucket]   [DynamoDB Table]   [CloudWatch + SNS]
```

### Flow

1. Client sends a `POST /buckets` request
2. API validates input
3. Lambda:

   * validates bucket_name
   * checks for duplicates
   * creates S3 bucket
   * stores metadata in DynamoDB
4. Response returned to client

---

## 🧰 Tech Stack

* Python / FastAPI
* AWS Lambda
* Amazon API Gateway (HTTP API)
* Amazon S3
* Amazon DynamoDB
* Terraform
* Boto3
* Mangum (ASGI adapter)
* GitHub Actions (CI/CD)

---

## 📦 API Endpoints

### Health Check

```
GET /
```

### Create Bucket

```
POST /buckets
```

#### Request Body

```json
{
  "team_name": "platform-team",
  "environment": "dev",
  "bucket_name": "platform-test-bucket-for-rich",
  "purpose": "testing s3 creation"
}
```

#### Behavior

* `bucket_name` must be globally unique
* Duplicate requests return:

```json
{
  "detail": "Bucket '<name>' already exists"
}
```

---

### Other Endpoints

```
GET /buckets
GET /buckets/{bucket_id}
PUT /buckets/{bucket_id}
DELETE /buckets/{bucket_id}
```

---

## ⚠️ API Design Note

`{bucket_id}` refers to the **internal request record ID (DynamoDB)**, not the S3 bucket name.

This reflects a platform pattern where:

* cloud resources ≠ tracking records

---

## ⚙️ Infrastructure (Terraform)

Resources provisioned:

* Lambda Function
* API Gateway
* DynamoDB Table
* IAM Roles & Policies
* CloudWatch Alarms
* SNS Topic

### Deploy locally

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## 🚀 CI/CD (GitHub Actions)

Pipeline:

```
.github/workflows/deploy.yml
```

### What it does

* Terraform fmt / validate / plan
* Builds Lambda package
* Deploys infrastructure
* Captures Terraform outputs
* Generates API usage guide artifact
* Publishes deployment summary with live endpoints

---

## 🌐 Live API Usage

After deployment, the pipeline outputs:

### Base API URL

```
https://<api-id>.execute-api.us-east-1.amazonaws.com
```

### Create Bucket Endpoint

```
https://<api-id>.execute-api.us-east-1.amazonaws.com/buckets
```

---

### Example curl

```bash
curl -X POST "https://<api-id>.execute-api.us-east-1.amazonaws.com/buckets" \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "platform-team",
    "environment": "dev",
    "bucket_name": "platform-test-bucket-for-rich",
    "purpose": "demo bucket creation"
  }'
```

---

### Example PowerShell

```powershell
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
```

---

## 🤖 AI Development Process

This project was developed using an AI-assisted workflow.

See:

* `AI_WORKFLOW.md` → how AI was used and validated
* `DECISIONS.md` → design decisions and tradeoffs

AI was used for:

* architecture design
* Terraform scaffolding
* API development
* CI/CD pipeline creation

All outputs were reviewed, validated, and refined manually.

---

## 📊 Observability

* CloudWatch logs for Lambda
* CloudWatch alarms for:

  * errors
  * duration
* SNS topic for notifications

---

## 🔐 IAM Permissions

Lambda permissions include:

* `s3:CreateBucket`
* `s3:PutBucketTagging`
* `s3:HeadBucket`
* `s3:GetBucketLocation`
* `dynamodb:PutItem`
* `dynamodb:GetItem`
* `dynamodb:Scan`

### Tradeoff

S3 permissions are broader due to dynamic bucket creation.

Future improvements:

* restrict via naming conventions
* apply condition-based policies

---

## 🧪 Demo Flow

1. Call `POST /buckets`
2. Bucket is created
3. Metadata stored in DynamoDB

Repeat request → duplicate error

Verify:

* S3 bucket exists
* DynamoDB record exists
* CloudWatch logs show activity

---

## 📄 Assignment Mapping

## Challenge Alignment

### ✅ AI Workflow

* documented in `AI_WORKFLOW.md`
* iterative and validated

### ✅ Terraform & CI/CD

* full IaC deployment
* automated pipeline

### ✅ Automation Service

* self-service API
* validation + error handling
* DynamoDB persistence

### ✅ Observability

* logging + alarms + SNS

### ✅ Documentation

* README
* DECISIONS.md
* AI_WORKFLOW.md
* architecture diagram

---

## 🔄 Future Improvements

* GitHub OIDC instead of static credentials
* Terraform modularization
* tighter IAM policies
* API authentication
* automated testing
* CloudWatch dashboards

---

## 🎯 Purpose

This project demonstrates:

* platform engineering principles
* infrastructure as code
* serverless architecture
* API-driven infrastructure provisioning
* observability practices
* AI-assisted development workflows

---

## 👤 Author

Richard Chia Ndum

---

## ⭐ Notes

This project simulates a real-world internal platform where developers can safely self-service infrastructure without direct cloud access.
