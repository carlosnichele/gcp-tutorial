from fastapi import FastAPI, Request, Depends, HTTPException
import os
import platform
import psutil
import socket
import time
import uuid
import secrets
import random
import string
import hashlib
from datetime import datetime, timezone
from crud_items import router as items_router
from database import engine
from models import Base
from logging_config import setup_logging
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token
from users import authenticate_user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
       raise HTTPException(status_code=401, detail="Invalid credentials")
       token = create_access_token({"sub": user["username"]})
       return {"access_token": token, "token_type": "bearer"}

setup_logging() # attiva il logging

app = FastAPI()

@app.get("/create-tables")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return {"status": "tables created"}

app.include_router(items_router)

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

    # Installed packages (best effort)
    try:
        import pkg_resources
        packages = sorted([str(p).split()[0] for p in pkg_resources.working_set])
    except Exception:
        packages = ["Unavailable"]

    latency_ms = round((time.time() - start) * 1000, 2)

    return {
        "app": app_info,
        "railway": railway_info,
        "system": system_info,
        "packages": packages[:20],
        "request_info": {
            "client": request.client.host,
            "latency_ms": latency_ms
        }
    }


@app.post("/echo")
async def echo(request: Request):
    body = await request.json()
    return {
        "received": body,
        "headers": dict(request.headers),
        "client": request.client.host
    }


@app.get("/uuid")
def generate_uuid():
    return {"uuid": str(uuid.uuid4())}


@app.get("/time")
def time_info():
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now().astimezone()

    return {
        "utc": now_utc.isoformat(),
        "local": now_local.isoformat(),
        "timestamp": int(now_utc.timestamp())
    }


@app.get("/ip")
def client_ip(request: Request):
    return {"client_ip": request.client.host}


@app.get("/headers")
def headers(request: Request):
    return dict(request.headers)


@app.get("/env")
def env():
    keys = ["RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "PORT"]
    return {k: os.getenv(k, "undefined") for k in keys}


@app.get("/random")
def random_utils():
    return {
        "int_1_100": random.randint(1, 100),
        "float_0_1": random.random(),
        "token_16": secrets.token_hex(16),
        "string_8": ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    }


@app.get("/calc")
def calc(a: float, b: float, op: str):
    if op == "add":
        result = a + b
    elif op == "sub":
        result = a - b
    elif op == "mul":
        result = a * b
    elif op == "div":
        result = a / b if b != 0 else "division by zero"
    else:
        result = "unknown operation"

    return {"a": a, "b": b, "op": op, "result": result}


@app.get("/hash")
def hash_string(text: str, algo: str = "sha256"):
    if algo == "sha256":
        h = hashlib.sha256(text.encode()).hexdigest()
    elif algo == "md5":
        h = hashlib.md5(text.encode()).hexdigest()
    else:
        return {"error": "unsupported algorithm"}

    return {"text": text, "algorithm": algo, "hash": h}


@app.get("/metrics")
def metrics():
    memory = psutil.virtual_memory()
    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0, 0, 0)

    return {
        "cpu_count": os.cpu_count(),
        "load_avg_1m": load_avg[0],
        "load_avg_5m": load_avg[1],
        "load_avg_15m": load_avg[2],
        "memory_total_mb": round(memory.total / 1024 / 1024, 2),
        "memory_used_percent": memory.percent,
        "uptime_seconds": int(time.time() - START_TIME)
    }
