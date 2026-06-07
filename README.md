# Project Title - Cloud ML & GenAI Fraud Detection Platform

# Overview

End-to-end cloud-native machine learning platform that trains a fraud detection model on AWS SageMaker and tracks model via MLflow, deploys it using containerized microservices on AWS ECS, processes requests asynchronously using Amazon SQS, enriches predictions with Amazon Bedrock LLM explanations, and manages infrastructure through Terraform and GitHub Actions CI/CD.

# Architecture

![Architecture](docs/architecture.png)

                                    +------------------+
                                    |     GitHub       |
                                    |   Source Code    |
                                    +--------+---------+
                                             |
                                             v
                                    +------------------+
                                    | GitHub Actions   |
                                    |    CI / CD       |
                                    +--------+---------+
                                             |
                                             v
                                    +------------------+
                                    |       ECR        |
                                    | Container Images |
                                    +--------+---------+
                                             |
                                             v
     ------------------------------------------------------------------
                            AWS ECS Fargate Cluster
     ------------------------------------------------------------------
         +--------------------+           +--------------------+
         |    API Service     |           |   Worker Service   |
         |      FastAPI       |           |    SQS Consumer    |
         +---------+----------+           +----------+---------+
                   |                                 |
                   | POST /predict                   |
                   |                                 |
                   v                                 |
         +--------------------+                      |
         |    Amazon SQS      |<---------------------+
         |   Request Queue    |
         +---------+----------+
                   |
                   v
         +--------------------+
         | Fraud Inference    |
         | Random Forest ML   |
         +---------+----------+
                   |
        +----------+-----------+
        |                      |
        v                      v
    +------------------+   +----------------------+
    | Amazon Bedrock   |   | Amazon S3            |
    | LLM Explanation  |   | Inference Logs       |
    +------------------+   | Audit Trail          |
                        | Job Status Files     |
                        +----------+-----------+
                                    |
                                    v
                            +------------------+
                            |  /status API     |
                            | Reads Results    |
                            +------------------+



# Infrastructure Layer
    +--------------------------------------------------------------+
    |                     Terraform (IaC)                          |
    +--------------------------------------------------------------+
            |              |              |              |
            v              v              v              v

        Amazon S3      Amazon SQS      Amazon ECR      ECS Cluster
            |              |               |               |
            +--------------+---------------+---------------+
                                            |
                                            v
                                    API + Worker Services

                                            |
                                            v
                                    Amazon Bedrock

                                            |
                                            v
                                    SageMaker
                                (Training Workflow)


# Tech Stack

ML

* Scikit-learn
* MLflow
* DVC

API

* FastAPI
* Pydantic

Cloud

* S3
* ECS Fargate
* ECR
* SQS
* Bedrock
* SageMaker

DevOps

* Terraform
* GitHub Actions
* Docker


## Features

* Fraud prediction
* Async processing
* LLM explanations
* S3 audit logging
* DLQ handling
* Infrastructure as Code
* Automated deployment                                


# Local Setup
```bash
git clone ..
docker compose up
```

# Deployment
```bash
cd terraform
terraform apply
```

```bash
git push
```

## Additional Documentation

| Document | Purpose |
|-----------|----------|
| docs/architecture.png | High-level system architecture |
| docs/Terraform appy.png | Terraform Deployment and Orchestration |
| docs/shutdown.md | Cost-control and shutdown procedures |
| docs/architecture_validation.md | End-to-end architecture validation |
| docs/add_sagemaker_s3_integration.md | SageMaker training and S3 integration |
| docs/add_reliability_monitoring.md | DLQ, monitoring, alarms, and operational hardening |


# ECS Deployment
![ECS Services](docs/screenshots/1.ECS-Cluster.png)

# Swagger
![Swagger](docs/screenshots/Swagger%20endpoint.png)
![Swagger](docs/screenshots/:predict%20part%201.png)
![Swagger](docs/screenshots/:predict%20part%202.png)

# Completed Inference
![Inference](docs/screenshots/:status:{request_id}%20part%201.png)
![Inference](docs/screenshots/:status:{request_id}%20part%202.png)

# GitHub Actions
![Actions](docs/screenshots/Screenshot%2011%20-%20GitHub%20Actions.png)

# Terraform
![Terraform](docs/screenshots/Terraform%20apply.png)