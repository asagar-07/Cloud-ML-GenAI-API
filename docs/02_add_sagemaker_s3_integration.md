Completed:

- Uploaded raw fraud dataset to S3
- Loaded dataset from S3 inside SageMaker notebook
- Trained RandomForest fraud detection model
- Logged local MLflow experiment under mlruns/
- Exported trained model as fraud_model.pkl
- Uploaded model artifact to S3 under models/fraud_model.pkl

Current artifact layout:

s3://cloud-ml-genai-api-proj-153058521958-us-east-1-an/

├── data/raw/creditcard.csv

└── models/fraud_model.pkl

MLflow:
- Local notebook tracking only for now
- Cloud-backed MLflow will be handled later