import json

import boto3
from botocore.exceptions import ClientError, BotoCoreError

import time
from typing import Dict, Any
from app.core.config import get_settings

settings = get_settings()

runtime = boto3.client('sagemaker-runtime', region_name=settings.aws_region)

def predict_with_sagemaker(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke SageMaker real-time endpoint for fraud prediction.
    Measures endpoint latency from worker/API side and includes it in the response."""

    start_time = time.perf_counter()

    try:
        response = runtime.invoke_endpoint(
            EndpointName=settings.sagemaker_endpoint_name,
            ContentType=settings.sagemaker_content_type,
            Body=json.dumps(payload)
        )
        endpoint_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response_body = response['Body'].read().decode("utf-8")
        parsed_response = json.loads(response_body)

        return {
            "success": True,
            "provider": "sagemaker",
            "endpoint_name": settings.sagemaker_endpoint_name,
            "endpoint_latency_ms": endpoint_latency_ms,
            "raw_response": parsed_response,
        }

    except (ClientError, BotoCoreError, json.JSONDecodeError, KeyError) as exc:
        endpoint_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "success": False,
            "provider": "sagemaker",
            "endpoint_name": settings.sagemaker_endpoint_name,
            "endpoint_latency_ms": endpoint_latency_ms,
            "error": str(exc),
        }