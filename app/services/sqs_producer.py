# serialize payload
# attach request_id
# attach timestamps
# push to queue

import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4
from app.core.logging import logger

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings

class SQSProducer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.queue_url = self.settings.sqs_queue_url
        self.aws_region = self.settings.aws_region

        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL is not configured")

        self.client = boto3.client("sqs", region_name=self.aws_region)

    def send_inference_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = str(uuid4())

        message_body = {
            "request_id": request_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "job_type": "fraud_inference",
            "payload": payload,
            "status": "QUEUED",
            "retry_count": 0,
        }

        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    "request_id": {
                        "StringValue": request_id,
                        "DataType": "String",
                    },
                    "job_type": {
                        "StringValue": "fraud_inference",
                        "DataType": "String",
                    },
                },
            )

            logger.info(
                "SQS message sent successfully",
                extra={
                    "request_id": request_id,
                    "message_id": response.get("MessageId"),
                    "queue_url": self.queue_url,
                },
            )

            return {
                "request_id": request_id,
                "message_id": response.get("MessageId"),
                "status": "QUEUED",
            }

        except (BotoCoreError, ClientError) as exc:
            logger.exception("Failed to send message to SQS")
            raise RuntimeError(f"Failed to send message to SQS: {exc}") from exc


sqs_producer = SQSProducer()