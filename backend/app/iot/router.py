from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.iot.models import SensorData
from app.iot.risk import calculate_risk
from app.auth.utils import decode_token
from app.database.connection import supabase
from typing import Optional

router = APIRouter(prefix="/iot", tags=["IoT Sensors"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ─── RECEIVE SENSOR DATA (from ESP32) ───────────────────────
@router.post("/sensors", status_code=201)
def receive_sensor_data(data: SensorData):
    """
    Endpoint called by ESP32 every X minutes.
    Receives temperature, humidity, soil moisture.
    Calculates risk and stores in database.
    """
    # Calculate disease risk
    risk_result = calculate_risk(data.temperature, data.humidity, data.soil_moisture)
    risk_level = risk_result["risk_level"]

    # Save sensor reading to database
    log = supabase.table("sensor_logs").insert({
        "farm_id": data.farm_id,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "soil_moisture": data.soil_moisture,
        "risk_level": risk_level
    }).execute()

    # If risk is medium or above — create an alert
    if risk_level in ["medium", "high", "critical"]:
        farm = supabase.table("farms").select("owner_id, name").eq("id", data.farm_id).execute()
        if farm.data:
            owner_id = farm.data[0]["owner_id"]
            farm_name = farm.data[0]["name"]

            supabase.table("alerts").insert({
                "farm_id": data.farm_id,
                "user_id": owner_id,
                "alert_type": "warning",
                "title": f"Environmental Risk Detected — {farm_name}",
                "message": risk_result["summary"],
                "risk_level": risk_level
            }).execute()

    log_id = log.data[0]["id"] if log.data else None

    return {
        "message": "Sensor data received",
        "risk_level": risk_level,
        "analysis": risk_result,
        "log_id": log_id
    }


# ─── GET LATEST SENSOR READING ──────────────────────────────
@router.get("/sensors/{farm_id}/latest")
def get_latest_reading(farm_id: str, user=Depends(get_current_user)):
    result = supabase.table("sensor_logs")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("recorded_at", desc=True)\
        .limit(1)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return result.data[0]


# ─── GET SENSOR HISTORY ─────────────────────────────────────
@router.get("/sensors/{farm_id}/history")
def get_sensor_history(
    farm_id: str,
    limit: int = Query(default=50, le=200),
    user=Depends(get_current_user)
):
    result = supabase.table("sensor_logs")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("recorded_at", desc=True)\
        .limit(limit)\
        .execute()

    return {
        "readings": result.data,
        "total": len(result.data)
    }


# ─── GET CURRENT RISK STATUS ────────────────────────────────
@router.get("/sensors/{farm_id}/risk")
def get_risk_status(farm_id: str, user=Depends(get_current_user)):
    """Get latest reading and its risk analysis"""
    result = supabase.table("sensor_logs")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("recorded_at", desc=True)\
        .limit(1)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No sensor data found")

    latest = result.data[0]
    risk_result = calculate_risk(
        latest["temperature"],
        latest["humidity"],
        latest["soil_moisture"]
    )

    return {
        "farm_id": farm_id,
        "last_reading": latest,
        "risk_analysis": risk_result
    }
