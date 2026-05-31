# sagemaker expects model artifacts in S3 in a model.tar.gz file -> fraud_model.pkl
# S3 location: s3://<bucket_name>/models/fraud-rf/model.tar.gz 
import json
import os
import joblib
import pandas as pd
import time

MODEL_FILENAME = 'fraud_model.pkl'

def model_fn(model_dir):
    "Loads model from SageMaker model directory."
    "SageMaker extracts the model.tar.gz file into model_dir."
    model_path = os.path.join(model_dir, MODEL_FILENAME)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = joblib.load(model_path)
    return model

def input_fn(request_body, request_content_type):
    "Parses incoming request payload, expected Content-Type: application/json."
    if request_content_type != 'application/json':
        raise ValueError(f"Unsupported content type: {request_content_type}")
    
    payload = json.loads(request_body)

    if isinstance(payload, dict):
        payload = [payload]  # Ensure payload is a list of records

    if not isinstance(payload, list):
        raise ValueError("Payload must be a JSON object or list of JSON objects.")
    
    df = pd.DataFrame(payload)
    return df

def predict_fn(input_data, model):
    "Run model prediction."

    start = time.perf_counter()

    predictions = model.predict(input_data)

    probabilities = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_data)
    
    inference_latency_ms = round((time.perf_counter() - start) * 1000, 2)

    results = []

    for idx, prediction in enumerate(predictions):
        fraud_probability = None

        if probabilities is not None:
            fraud_probability = float(probabilities[idx][1])

        results.append(
            {
                "prediction": int(prediction),
                "prediction_label": "FRAUD" if int(prediction) == 1 else "NOT_FRAUD",
                "fraud_probability": fraud_probability,
                "target": "Class",
                "model_stage": "SageMaker Random Forest Endpoint",
                "model_type": type(model).__name__,
                "inference_latency_ms": inference_latency_ms,
            }
        )

    return results

def output_fn(prediction_output, response_content_type):
    "Formats prediction response."

    if response_content_type != 'application/json':
        raise ValueError(f"Unsupported response content type: {response_content_type}")

    return json.dumps(
        {
            "success": True,
            "predictions": prediction_output,
        }
    )
