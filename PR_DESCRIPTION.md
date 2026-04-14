\## Summary



This PR improves the Platform Self-Service API by strengthening security, documenting the AI-native development workflow, and enhancing infrastructure quality.



Changes focus on aligning the project with platform engineering best practices and assignment requirements.



\---



\## Key Changes



\### 🔐 IAM Hardening

\- Scoped DynamoDB permissions to specific table ARN

\- Scoped CloudWatch logs to Lambda log group

\- Reduced use of wildcard permissions where possible

\- Documented S3 permission tradeoffs for dynamic bucket creation



\### 🤖 AI-Native Workflow

\- Added `CHATGPT.md` to document AI usage, rules, and workflow

\- Captured how AI was used for:

&#x20; - architecture design

&#x20; - Terraform generation

&#x20; - debugging Lambda packaging issues

&#x20; - CI/CD pipeline creation

\- Documented where AI required correction and validation



\### 🏗️ Terraform Improvements

\- Added validation steps (`terraform fmt`, `validate`)

\- Improved structure for maintainability

\- Prepared groundwork for modularization



\### 📊 Observability Enhancements

\- Improved logging clarity

\- Ensured alarms and SNS notifications are correctly configured



\### 📄 Documentation Updates

\- Updated README to better map assignment requirements

\- Expanded design rationale around:

&#x20; - Lambda vs ECS

&#x20; - DynamoDB vs relational DB

&#x20; - IAM tradeoffs



\---



\## AI-Assisted Development



AI (ChatGPT) was used as a development collaborator throughout this project.



\### Where AI helped:

\- Rapid Terraform scaffolding

\- Debugging AWS Lambda packaging/import issues

\- Designing API structure and validation

\- Generating CI/CD pipeline



\### Where manual intervention was required:

\- IAM policy scoping (AI suggested overly broad permissions)

\- S3 behavior nuances (especially in us-east-1)

\- Terraform dependency and resource ordering

\- Ensuring production-safe decisions



\### Validation approach:

\- Manual AWS verification (S3, DynamoDB, CloudWatch)

\- Terraform validation (`fmt`, `validate`, `plan`)

\- End-to-end API testing



\---



\## Tradeoffs \& Decisions



\- \*\*S3 IAM scoping\*\*: Due to dynamic bucket creation, full resource-level restriction is limited. Mitigated via:

&#x20; - strict naming conventions

&#x20; - input validation

&#x20; - documentation of constraints



\- \*\*Lambda over ECS\*\*: Chosen for simplicity, cost-efficiency, and faster iteration for MVP



\- \*\*DynamoDB over RDS\*\*: Chosen for simplicity and serverless alignment



\---



\## Testing



\- Verified bucket creation via API

\- Verified duplicate bucket handling

\- Confirmed DynamoDB records are written

\- Validated CloudWatch logs and alarms



\---



\## Next Steps



\- Replace AWS credentials with GitHub OIDC

\- Further modularize Terraform

\- Add automated tests to CI pipeline

\- Add API authentication (e.g., API Gateway authorizer)

\- Add CloudWatch dashboards



\---



\## Notes



This PR is intentionally left open to demonstrate AI-assisted development workflow, iteration, and design evolution.


