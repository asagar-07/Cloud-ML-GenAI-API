from fastapi import APIRouter, HTTPException

from app.services.bedrock_service import BedrockService
from app.schemas.genai import GenAIRequest, GenAIResponse

router = APIRouter(prefix="/genai", tags=["GenAI"])

bedrock_service = BedrockService()

@router.post("/generate", response_model=GenAIResponse)
def generate_text(request: GenAIRequest):
    result = bedrock_service.generate_response(request.prompt)

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["error"],
        )

    return result