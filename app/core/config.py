from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Cloud ML & GenAI Deploy API"
    app_env: str = "dev"
    app_version: str = "0.1.0"

    enable_file_logging: bool = True
    log_level: str = "INFO"
    
    # AWS
    aws_region: str
    s3_bucket: str
    ecr_repo: str
    ecs_service_name: str
    ecs_container_port: int
    mlflow_tracking_uri: str

    # SQS
    sqs_queue_name: str | None = None
    sqs_queue_url: str | None = None
    sqs_dlq_name: str | None = None
    sqs_dlq_url: str | None = None

    # SageMaker
    use_sagemaker_endpoint: bool = False
    sagemaker_endpoint_name: str = ""
    sagemaker_content_type: str = "application/json"

    # Bedrock
    bedrock_model_provider: str 
    bedrock_model_id: str
    bedrock_max_tokens: int 
    bedrock_temperature: float 
    bedrock_top_p: float
    bedrock_top_k: int 
     
    model_config = SettingsConfigDict(
         env_file=(".env", ".env.aws"),
        env_file_encoding = "utf-8",
        extra = "ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()