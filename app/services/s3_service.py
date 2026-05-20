import json
from datetime import datetime, timezone
from typing import Optional
import os

import boto3

s3_client = boto3.client("s3")

bucket_name = os.getenv("S3_BUCKET")

def log_inference(job_id: str, payload: dict, prediction_result: dict, latency_ms: float, bedrock_response: Optional[dict] = None):
    if not bucket_name:
        raise ValueError("S3_BUCKET environment variable is not set")

    current_time = datetime.now(timezone.utc)

    log_data = {
        "job_id": job_id,
        "payload": payload,
        "prediction_result": prediction_result,
        "latency_ms": latency_ms,
        "timestamp": current_time.isoformat(),
        "bedrock_response": bedrock_response
    }

    log_key = (
        f"logs/inference/"
        f"{current_time.strftime('%Y/%m/%d')}/"
        f"{job_id}.json"
    )

    s3_client.put_object(
        Bucket=bucket_name,
        Key=log_key,
        Body=json.dumps(log_data).encode("utf-8"),
        ContentType="application/json",
    )

    return f"s3://{bucket_name}/{log_key}"

def get_job_from_s3(job_id: str) -> Optional[dict]:
    if not bucket_name:
        raise ValueError("S3_BUCKET environment variable is not set")

    current_time = datetime.now(timezone.utc)
    
    prefix = (f"logs/inference/"
              f"{current_time.strftime('%Y/%m/%d')}/")
    
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" not in response:
        return None

    for obj in response["Contents"]:
        key = obj["Key"]

        if key.endswith(f"{job_id}.json"):
            log_object = s3_client.get_object(Bucket=bucket_name, Key=key)
            return json.loads(log_object["Body"].read().decode("utf-8"))
    
    return None