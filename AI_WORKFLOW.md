# 🤖 AI-Assisted Development Workflow

This project was developed using an AI-assisted workflow, where ChatGPT was used as a collaborative development partner rather than a code generator.

---

## 🧠 How AI Was Used

AI was used throughout the development lifecycle:

### 1. Architecture Design
- Proposed initial serverless architecture (API Gateway → Lambda → S3 + DynamoDB)
- Helped validate design choices for a platform-style service

### 2. Terraform Development
- Generated initial Terraform configurations
- Suggested resource relationships and dependencies
- Assisted with backend configuration (S3 state, remote state)

### 3. API Development (FastAPI)
- Scaffolded endpoints for:
  - POST /buckets
  - GET /buckets
  - DELETE /buckets/{id}
- Suggested Pydantic models for input validation

### 4. CI/CD Pipeline
- Helped design GitHub Actions workflow
- Assisted with:
  - Lambda packaging
  - Terraform automation
  - Deployment steps

---

## ⚠️ Where AI Was Incorrect (and Fixed)

AI was not always correct and required validation:

### IAM Policies
- Initial suggestion used overly permissive policies (`Resource = "*"`)
- Corrected to follow least-privilege principles where possible

### API Logic
- Early logic did not correctly handle duplicate bucket creation
- Added explicit checks using `head_bucket`

### DynamoDB ID Usage
- Initial design mixed bucket names with internal IDs
- Refactored to clearly separate:
  - `bucket_name` (S3 resource)
  - `bucket_id` (DynamoDB record ID)

---

## 🔍 Validation Process

All AI-generated code was:

- Reviewed manually
- Tested locally using FastAPI
- Validated against AWS behavior
- Iteratively refined through debugging

---

## 🔄 Iteration Workflow

Typical development loop:

1. Ask AI for initial implementation
2. Review and modify output
3. Test locally or in AWS
4. Identify issues or edge cases
5. Refine implementation with AI assistance
6. Repeat until stable

---

## 🚀 Improvements to AI Workflow

If extended further:

- Use structured prompts for consistency
- Add automated validation (linting, testing)
- Integrate AI into CI for PR review
- Use tools like Claude Code or Cursor for deeper integration

---

## 🎯 Key Takeaway

AI accelerated development significantly, but success depended on:

- critical evaluation
- validation of outputs
- iterative refinement

This reflects a real-world AI-native engineering workflow.