from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionRequest
from app.services.job_store import create_job
from app.services.sqs_producer import SQSProducer


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