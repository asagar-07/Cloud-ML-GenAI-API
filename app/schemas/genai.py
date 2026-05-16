from pydantic import BaseModel, Field

class GenAIRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)


class GenAIResponse(BaseModel):
    success: bool
    model_id: str
    response: str | None
    latency_seconds: float | None
    error: str | None = None
