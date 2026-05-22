import json
import logging
import time
from typing import Any, Dict
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings
from app.core.logging import logger
from app.services.job_store import update_job_status, complete_job, fail_job
from app.services.prediction_service import predict_fraud
from app.services.s3_service import log_inference
from app.services.bedrock_service import BedrockService

settings = get_settings()

class SQSWorker:
    def __init__(self) -> None:
        self.queue_url = settings.sqs_queue_url
        self.region = settings.aws_region
        self.wait_time_seconds = 20
        self.max_messages = 1

        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL is not configured")

        self.sqs_client = boto3.client("sqs", region_name=self.region)
        self.bedrock_service = BedrockService()

    def poll_forever(self) -> None:
        logger.info("SQS worker started")

        while True:
            try:
                messages = self.receive_messages()

                if not messages:
                    logger.info("No messages found. Polling again...")
                    continue

                for message in messages:
                    self.process_message(message)

            except KeyboardInterrupt:
                logger.info("SQS worker stopped manually")
                break

            except Exception as exc:
                logger.exception("Unexpected worker loop error: %s", exc)
                time.sleep(5)

    def receive_messages(self) -> list[Dict[str, Any]]:
        response = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=self.max_messages,
            WaitTimeSeconds=self.wait_time_seconds,
            MessageAttributeNames=["All"],
            AttributeNames=["ApproximateReceiveCount"],
        )

        return response.get("Messages", [])

    def process_message(self, message: Dict[str, Any]) -> None:
        # This is to force worker failure for testing DLQ functionality. Set environment variable FORCE_WORKER_FAILURE=true to enable.
        logger.info("Worker received message")

        force_failure = os.getenv("FORCE_WORKER_FAILURE", "false").lower() == "true"
        logger.info("FORCE_WORKER_FAILURE=%s", force_failure)

        if force_failure:
            error_message = "Forced worker failure for DLQ testing"
            fail_job(request_id, error_message)
            logger.error(error_message)
            raise RuntimeError(error_message)

        # existing processing code will not be executed when failure is forced
        receipt_handle = message["ReceiptHandle"]
        body = json.loads(message["Body"])

        request_id = body.get("request_id")
        payload = body.get("payload")
        receive_count = message.get("Attributes", {}).get("ApproximateReceiveCount")

        logger.info(
            "Processing SQS message",
            extra={
                "request_id": request_id,
                "receive_count": receive_count,
            },
        )

        try:
            update_job_status(request_id, "PROCESSING")

            prediction_result = predict_fraud(payload)

            llm_prompt = f"""
            You are an ML fraud detection assistant.
            Explain the fraud prediction result below in simple business terms.
            Input transaction data:
            {json.dumps(payload, indent=2)}
            Model prediction result:
            {json.dumps(prediction_result, indent=2)}
            Provide:
            1. Final prediction
            2. Fraud probability
            3. Key risk interpretation
            4. Short explanation for a non-technical user
            """
            bedrock_response = self.bedrock_service.generate_response(llm_prompt)

            final_result = {
                "request_id": request_id,
                "status": "COMPLETED",
                "payload": payload,
                "prediction_result": prediction_result,
                "bedrock_response": bedrock_response,
                "latency_ms": prediction_result.get("latency_ms", 0),
            }

            log_inference(
                job_id=request_id,
                payload=payload,
                prediction_result={
                    **prediction_result,
                    "bedrock_response": bedrock_response,
                    "request_id": request_id,
                    "status": "COMPLETED",
                },
                latency_ms=prediction_result.get("latency_ms", 0),
            )

            complete_job(request_id, final_result)

            self.delete_message(receipt_handle)

            logger.info(
                "Message processed and deleted successfully",
                extra={"request_id": request_id},
            )

        except Exception as exc:
            error_message = str(exc)
            logger.exception(
                f"Message processing failed for request_id={request_id}, error={error_message}. Message will not be deleted."
                )
            try:
                fail_job(request_id, error_message)
            except Exception:
                logger.exception("Failed to update job status after processing error")

            # Note:
            # Failed Messages will not be deleted.
            # SQS will retry after visibility timeout.
            # Moves to DLQ after maxReceiveCount.
            raise

    def delete_message(self, receipt_handle: str) -> None:
        self.sqs_client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )


if __name__ == "__main__":
    worker = SQSWorker()
    worker.poll_forever()