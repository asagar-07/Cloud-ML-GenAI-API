from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionRequest
from app.services.job_store import create_job, get_job
from app.services.sqs_producer import SQSProducer
from app.services.s3_service import get_job_from_s3


router = APIRouter(prefix="/predict", tags=["Prediction"])

sqs_producer = SQSProducer()


@router.post("/async")
async def predict_async(request: PredictionRequest):
    try:
        payload_dict = request.model_dump()
        queued_job = sqs_producer.send_inference_job(payload=payload_dict)

        create_job(queued_job["request_id"], payload_dict)

        return {
            "status": "QUEUED",
            "message": "Inference request accepted and queued for async processing.",
            "request_id": queued_job["request_id"],
            "message_id": queued_job["message_id"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to queue inference request: {str(exc)}", )
    

@router.get("/status/{request_id}")
async def get_status(request_id: str):
    # Retrieve from S3 log if not found in job store
    job = get_job_from_s3(request_id)

    if not job:
        return {
            "request_id": request_id,
            "status": "PENDING",
            "message": "Job has been accepted but result is not available yet. May be queued or processing. Please check back later.",
            "result": None,
        }

    return {
        "request_id": request_id,
        "status": job.get("status", "COMPLETED"),
        "message": "Job completed successfully.",
        "result": job,
    }