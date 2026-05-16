import json
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.core.logging import logger


class BedrockService:
    def __init__(self):
        self.settings = get_settings()

        self.client = boto3.client("bedrock-runtime", region_name=self.settings.aws_region)
        self.model_id = self.settings.bedrock_model_id
        self.max_tokens = self.settings.bedrock_max_tokens
        self.temperature = self.settings.bedrock_temperature
        self.top_p = self.settings.bedrock_top_p
        self.provider = self.settings.bedrock_model_provider

    def generate_response(self, input_text: str) -> dict[str, Any]:

        try:
            request_body = self._build_request(input_text)
            start_time = time.time()

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json",
            )

            latency = round(time.time() - start_time, 4)
            response_body = json.loads(response["body"].read())
            output_text = self._parse_response(response_body)

            logger.info(
                "Bedrock invocation successful | provider=%s | model_id=%s | latency=%s",
                self.provider,
                self.model_id,
                latency,
            )

            return {
                "success": True,
                "status": "COMPLETED",
                "provider": self.provider,
                "model_id": self.model_id,
                "response": output_text,
                "latency_seconds": latency,
            }

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code in ["ThrottlingException", "TooManyRequestsException"]:
                logger.warning(
                    "Bedrock throttled | provider=%s | model_id=%s | error_code=%s",
                    self.provider,
                    self.model_id,
                    error_code,
                )

                return {
                    "success": False,
                    "status": "THROTTLED",
                    "provider": self.provider,
                    "model_id": self.model_id,
                    "error_code": error_code,
                    "error": error_message,
                    "response": None,
                    "latency_seconds": None,
                }

            logger.exception("AWS Bedrock ClientError")

            return {
                "success": False,
                "status": "FAILED",
                "provider": self.provider,
                "model_id": self.model_id,
                "error_code": error_code,
                "error": error_message,
                "response": None,
                "latency_seconds": None,
            }
        
        
        except Exception as e:
            logger.exception("Unexpected Bedrock invocation error")
            return {
                "success": False,
                "provider": self.provider,
                "model_id": self.model_id,
                "error": str(e),
                "response": None,
                "latency_seconds": None,
            }

    def _build_request(self, input_text: str) -> dict[str, Any]:

        if self.provider == "anthropic":
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": input_text}],
                    }
                ],
            }

        if self.provider == "amazon_nova":
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": input_text}],
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                },
            }

        if self.provider == "meta":
            return {
                "prompt": input_text,
                "max_gen_len": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }

        raise ValueError(f"Unsupported Bedrock provider: {self.provider}")

    def _parse_response(self, response_body: dict[str, Any]) -> str:
        if self.provider == "anthropic":
            return response_body["content"][0]["text"]

        if self.provider == "amazon_nova":
            return response_body["output"]["message"]["content"][0]["text"]
        
        if self.provider == "meta":
            return response_body["generation"]

        raise ValueError(f"Unsupported Bedrock provider: {self.provider}")