from fastapi import FastAPI
import os
import platform
import psutil
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
    # System info
    cpu_count = os.cpu_count()
    memory = psutil.virtual_memory()

    # Railway environment variables
    railway_info = {
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
        "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
        "service_id": os.getenv("RAILWAY_SERVICE_ID", "unknown"),
        "region": os.getenv("RAILWAY_REGION", "unknown"),
        "port": os.getenv("PORT", "unknown"),
    }

    # App info
    app_info = {
        "name": "FastAPI on Railway",
        "version": "1.0.0",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "timezone": datetime.now().astimezone().tzinfo.__str__(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }

    # System resources
    system_info = {
        "cpu_count": cpu_count,
        "memory_total_mb": round(memory.total / 1024 / 1024, 2),
        "memory_available_mb": round(memory.available / 1024 / 1024, 2),
        "memory_usage_percent": memory.percent,
    }

    return {
        "app": app_info,
        "railway": railway_info,
        "system": system_info,
    }
