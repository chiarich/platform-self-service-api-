# 🧠 Design Decisions

## 1. Serverless Architecture

**Decision:** Use AWS Lambda + API Gateway

**Why:**
- Low operational overhead
- Scales automatically
- Ideal for event-driven API

**Alternative:**
- ECS Fargate (more control, more complexity)

---

## 2. S3 Buckets Created at Runtime

**Decision:** Buckets created via API, not Terraform

**Why:**
- Enables self-service platform behavior
- Reflects real-world platform design

**Tradeoff:**
- Buckets are not tracked in Terraform state
- Must be managed separately

---

## 3. DynamoDB for Metadata

**Decision:** Store request metadata in DynamoDB

**Why:**
- Simple, serverless, scalable
- No schema management overhead

---

## 4. API Design

**Decision:** Separate bucket_name and bucket_id

**Why:**
- Avoid confusion between cloud resources and internal records
- Aligns with platform API design patterns

---

## 5. CI/CD with GitHub Actions

**Decision:** Use GitHub Actions for deployment

**Why:**
- Native integration with repo
- Supports Terraform automation
- Enables reproducible deployments

---

## 6. Observability

**Decision:** Use CloudWatch + SNS

**Why:**
- Native AWS monitoring
- Simple alerting for errors and performance

---

## 7. IAM Tradeoff

**Decision:** Allow broader S3 permissions

**Why:**
- Bucket names are dynamic
- Hard to scope ahead of time

**Future Improvement:**
- Use naming constraints + condition keys
- Apply permission boundaries

---

## 🎯 Summary

Design prioritized:
- simplicity
- scalability
- developer self-service
- real-world platform patterns