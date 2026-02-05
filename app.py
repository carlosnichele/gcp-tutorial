from fastapi import FastAPI, Request
import os
import platform
import psutil
import socket
import time
from datetime import datetime, timezone

app = FastAPI()

START_TIME = time.time()

def get_uptime():
    seconds = int(time.time() - START_TIME)
    return {
        "seconds": seconds,
        "minutes": round(seconds / 60, 2),
        "hours": round(seconds / 3600, 2)
    }

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
def info(request: Request):
    start = time.time()

    # System info
    cpu_count = os.cpu_count()
    memory = psutil.virtual_memory()
    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)

    # Network info
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # Railway environment variables
    railway_info = {
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
        "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
        "service_id": os.getenv("RAILWAY_SERVICE_ID", "unknown"),
        "region": os.getenv("RAILWAY_REGION", "unknown"),
        "port": os.getenv("PORT", "unknown"),
        "commit_sha": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown"),
    }

    # App info
    app_info = {
        "name": "FastAPI on Railway",
        "version": "1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timezone": datetime.now().astimezone().tzinfo.__str__(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": hostname,
        "ip_address": ip_address,
        "uptime": get_uptime(),
    }

    # System resources
    system_info = {
        "cpu_count": cpu_count,
        "load_average": {
            "1min": load_avg[0],
            "5min": load_avg[1],
            "15min": load_avg[2],
        },
        "memory_total_mb": round(memory.total / 1024 / 1024, 2),
        "memory_available_mb": round(memory.available / 1024 / 1024, 2),
        "memory_usage_percent": memory.percent,
    }

    # Installed packages (top-level only)
    try:
        import pkg_resources
        packages = sorted([str(p).split()[0] for p in pkg_resources.working_set])
    except:
        packages = ["Unavailable"]

    # Response time
    latency_ms = round((time.time() - start) * 1000, 2)

    return {
        "app": app_info,
        "railway": railway_info,
        "system": system_info,
        "packages": packages[:20],  # primi 20 pacchetti
        "request_info": {
            "client": request.client.host,
            "latency_ms": latency_ms
        }
    }
