from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.bedrock_service import BedrockService

router = APIRouter(prefix="/genai", tags=["GenAI"])

bedrock_service = BedrockService()

class GenAIRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class GenAIResponse(BaseModel):
    success: bool
    model_id: str
    response: str | None
    latency_seconds: float | None
    error: str | None = None


@router.post("/generate", response_model=GenAIResponse)
def generate_text(request: GenAIRequest):
    result = bedrock_service.generate_response(request.prompt)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["error"],
        )

    return result