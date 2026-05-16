import uuid
from fastapi import APIRouter, BackgroundTasks

from app.schemas.prediction import PredictionRequest
from app.services.job_store import create_job, update_job_status, complete_job, fail_job
from app.services.prediction_service import predict_fraud
from app.services.s3_service import log_inference
from app.services.bedrock_service import BedrockService


router = APIRouter(prefix="/predict", tags=["Prediction"])

bedrock_service = BedrockService()

def process_prediction_job(job_id: str, payload: dict) -> None:
    try:
        update_job_status(job_id, "PROCESSING")

        prediction_result = predict_fraud(payload)

        prompt = f"""
        Fraud Detection Analysis
        
        Prediction Result:
        {prediction_result}

        Transaction Payload:
        {payload}

        Provide a short explanation about why this transaction may be considered fraudulent or not.
        """

        bedrock_response = bedrock_service.generate_response(prompt)

        s3_log_path = log_inference(
            job_id=job_id,
            payload=payload,
            prediction_result=prediction_result,
            latency_ms=prediction_result["latency_ms"],
            bedrock_response=bedrock_response,
            )

        result = {
            "prediction_result": prediction_result,
            "llm_status": bedrock_response.get("status", "UNKNOWN"),
            "llm_response": bedrock_response.get("response"),
            "bedrock_result": bedrock_response,
            "s3_log_path": s3_log_path,
        }
        
        complete_job(job_id, result)

    except Exception as exc:
        fail_job(job_id, str(exc))


@router.post("/async")
async def predict_async(payload: PredictionRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    payload_dict = payload.model_dump()

    create_job(job_id, payload_dict)

    background_tasks.add_task(process_prediction_job, job_id, payload_dict)

    return {
        "job_id": job_id,
        "status": "QUEUED",
        "message": "Prediction request received and is being processed in the background.",
    }