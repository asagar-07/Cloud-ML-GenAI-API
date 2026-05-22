#  Reliability and Monitoring

## DLQ Failure Testing

- Added FORCE_WORKER_FAILURE worker flag.
- Rebuilt Docker image for linux/amd64.
- Pushed image to ECR.
- Registered new ECS task definition revision.
- Updated worker service with FORCE_WORKER_FAILURE=true for test.
- Confirmed worker raised forced exception.
- Confirmed SQS retry and DLQ movement.
- Confirmed DLQ message contained request_id.
- Validated dlq_inspector.py.
- Restored worker with FORCE_WORKER_FAILURE=false.

## Known Operational Notes

- Docker image must be built for linux/amd64 for ECS Fargate.
- Local Mac ARM builds can fail with:
  `image Manifest does not contain descriptor matching platform linux/amd64`