# CHATGPT.md

## AI Tool Used
ChatGPT (OpenAI)

## Purpose
Used as a development collaborator for:
- Designing architecture (Lambda + API Gateway + DynamoDB)
- Generating Terraform templates
- Debugging Lambda packaging issues
- Improving IAM policies and security posture
- Designing CI/CD pipeline (GitHub Actions)
- Enhancing observability (CloudWatch, SNS)

## Development Workflow

### 1. Problem Definition
I describe the problem or feature to ChatGPT with:
- current code or error
- expected behavior

### 2. Iteration
ChatGPT suggests:
- code
- Terraform updates
- debugging steps

I:
- review suggestions critically
- test locally or in AWS
- refine prompts when output is incorrect

### 3. Validation
- Run Terraform commands (`fmt`, `validate`, `plan`)
- Deploy via GitHub Actions
- Test API manually
- Verify AWS resources (S3, DynamoDB, CloudWatch)

## Rules Given to ChatGPT
- Prefer least-privilege IAM
- Avoid hardcoded secrets
- Use AWS best practices
- Keep code simple and readable
- Validate all API inputs
- Do not assume AWS defaults without explanation

## Where AI Helped Most
- Fixing Lambda dependency packaging issues
- Designing API structure with FastAPI
- Building Terraform resources quickly
- Debugging AWS service integration issues

## Where AI Needed Correction
- Incorrect IAM scoping suggestions
- Assumptions about S3 bucket behavior in us-east-1
- Overly broad permissions
- Missing dependency packaging steps

## Lessons Learned
- AI accelerates development but must be verified
- AWS-specific behavior often requires manual correction
- Iterative prompting improves output quality