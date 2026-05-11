# Architecture Validation

## Target Flow

S3 raw data
→ SageMaker training
→ model artifacts to S3 + MLflow
→ ECR Docker image
→ ECS Express Mode Deployment
→ Bedrock LLM inference
→ CloudWatch/S3 logs

## Validation Status

- [x] AWS account created
- [x] MFA/security setup completed
- [x] AWS CLI installed/configured
- [x] S3 bucket created
- [x] ECR repository created
- [x] Docker image pushed to ECR
- [x] SageMaker enabled
- [x] SageMaker execution role created
- [x] SageMaker read/write access to S3 validated
- [x] Bedrock access attempted and IAM/connection validated
- [x] Bedrock runtime throttled due to temporary quota
- [x] `.env.aws` created

## Current Architecture Decision

Use:

S3 → SageMaker → S3/MLflow → ECR → ECS Express Mode → Bedrock → CloudWatch/S3


### Amazon ECR

Stores Docker container images for deployment.

### Amazon ECS Express Mode

Hosts and deploys the FastAPI application container.

### Amazon Bedrock

Provides managed LLM inference through boto3 API calls.

### Amazon CloudWatch

Stores:

- application logs

- container logs

- monitoring metrics

- deployment/runtime diagnostics

---

## Notes

- SageMaker training jobs will be preferred over local training.

- FastAPI application will be containerized using Docker.

- Docker images will be stored in Amazon ECR.

- ECS Express Mode replaces AWS App Runner for new AWS accounts.

- Bedrock will be called directly from FastAPI using boto3.

- Model artifacts will be stored in S3 and loaded by the API service.

- Shutting down SageMaker apps, training jobs, ECS services, and unused cloud resources after testing sessions for cost control.