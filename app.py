from fastapi import FastAPI
import os
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Hello from Railway!",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/info")
def info():
    return {
        "app": "FastAPI on Railway",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
        "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
