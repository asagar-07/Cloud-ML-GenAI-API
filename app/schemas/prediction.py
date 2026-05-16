from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    Time: float = Field(..., description="Transaction time in incremental seconds from the first transaction in the dataset")
    V1: float = Field(..., description="Feature V1")
    V2: float = Field(..., description="Feature V2")
    V3: float = Field(..., description="Feature V3")
    V4: float = Field(..., description="Feature V4")
    V5: float = Field(..., description="Feature V5")
    V6: float = Field(..., description="Feature V6")
    V7: float = Field(..., description="Feature V7")
    V8: float = Field(..., description="Feature V8")
    V9: float = Field(..., description="Feature V9")
    V10: float = Field(..., description="Feature V10")
    V11: float = Field(..., description="Feature V11")
    V12: float = Field(..., description="Feature V12")
    V13: float = Field(..., description="Feature V13")
    V14: float = Field(..., description="Feature V14")
    V15: float = Field(..., description="Feature V15")
    V16: float = Field(..., description="Feature V16")
    V17: float = Field(..., description="Feature V17")
    V18: float = Field(..., description="Feature V18")
    V19: float = Field(..., description="Feature V19")
    V20: float = Field(..., description="Feature V20")
    V21: float = Field(..., description="Feature V21")
    V22: float = Field(..., description="Feature V22")
    V23: float = Field(..., description="Feature V23")
    V24: float = Field(..., description="Feature V24")
    V25: float = Field(..., description="Feature V25")
    V26: float = Field(..., description="Feature V26")
    V27: float = Field(..., description="Feature V27")
    V28: float = Field(..., description="Feature V28")
    Amount: float = Field(..., description="Transaction amount")   

class PredictionResponse(BaseModel):
    prediction: int
    prediction_label: str
    fraud_probability: float | None
    target: str
    model_stage: str
    model_type: str
    latency_ms: float
