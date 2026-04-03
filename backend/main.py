from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys

print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}")

try:
    from app.auth.router import router as auth_router
    from app.farm.router import router as farm_router
    from app.iot.router import router as iot_router
    from app.disease.router import router as disease_router
    from app.alerts.router import router as alerts_router
    from app.admin.router import router as admin_router
    print("Auth router loaded OK")
    print("Farm router loaded OK")
    print("IoT router loaded OK")
    print("Disease router loaded OK")
    print("Alerts router loaded OK")
    print("Admin router loaded OK")
except Exception as e:
    print(f"ROUTER FAILED: {e}")
    auth_router = None
    farm_router = None
    iot_router = None
    disease_router = None
    alerts_router = None
    admin_router = None

load_dotenv()

app = FastAPI(
    title="Tomato Disease Detection System",
    description="AI & IoT-Based System for Early Detection and Prevention of Tomato Diseases",
    version="1.0.0"
)

# CORS - allows Flutter and Next.js to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:44280",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
if auth_router:
    app.include_router(auth_router)
    print("Auth router registered")
if farm_router:
    app.include_router(farm_router)
    print("Farm router registered")
if iot_router:
    app.include_router(iot_router)
    print("IoT router registered")
if disease_router:
    app.include_router(disease_router)
    print("Disease router registered")
if alerts_router:
    app.include_router(alerts_router)
    print("Alerts router registered")
if admin_router:
    app.include_router(admin_router)
    print("Admin router registered")


@app.get("/")
def root():
    return {
        "message": "Tomato Disease Detection System API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
