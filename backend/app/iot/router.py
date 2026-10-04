from fastapi import APIRouter, HTTPException, Query
from app.iot.models import SensorData
from app.iot.risk import calculate_risk
from app.database.connection import supabase
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/iot", tags=["IoT Sensors"])


# ─── RECEIVE SENSOR DATA (from ESP32) ───────────────────────
@router.post("/sensors", status_code=201)
def receive_sensor_data(data: SensorData):
    """
    Endpoint called by ESP32 every X minutes.
    Receives temperature, humidity, soil moisture.
    Calculates risk and stores in database.
    NO AUTHENTICATION REQUIRED
    """
    # Validate farm exists
    farm = supabase.table("farms").select("id, owner_id, name").eq("id", data.farm_id).execute()
    if not farm.data:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Calculate disease risk
    risk_result = calculate_risk(data.temperature, data.humidity, data.soil_moisture)
    risk_level = risk_result["risk_level"]

    # Save sensor reading to database
    log = supabase.table("sensor_logs").insert({
        "farm_id": data.farm_id,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "soil_moisture": data.soil_moisture,
        "risk_level": risk_level,
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    # If risk is medium or above — create an alert with predictions
    if risk_level in ["medium", "high", "critical"]:
        owner_id = farm.data[0]["owner_id"]
        farm_name = farm.data[0]["name"]

        # Build detailed message with disease predictions
        predicted_diseases = risk_result.get("predicted_diseases", [])
        message = risk_result["summary"]

        if predicted_diseases:
            message += "\n\n📋 PREDICTED DISEASES:\n"
            for disease_info in predicted_diseases:
                message += f"\n🦠 {disease_info['disease']} ({disease_info['likelihood']} risk)\n"
                message += f"Timeline: {disease_info['timeline']}\n"
                message += "Actions:\n"
                for rec in disease_info['recommendations'][:3]:  # First 3 recommendations
                    message += f"  • {rec}\n"

        supabase.table("alerts").insert({
            "farm_id": data.farm_id,
            "user_id": owner_id,
            "alert_type": "prediction" if predicted_diseases else "warning",
            "title": f"{'🚨 URGENT: ' if risk_level == 'critical' else '⚠️ '}Disease Risk Alert — {farm_name}",
            "message": message,
            "risk_level": risk_level,
            "predicted_diseases": predicted_diseases,
            "sent_at": datetime.now(timezone.utc).isoformat()
        }).execute()

    log_id = log.data[0]["id"] if log.data else None

    return {
        "message": "Sensor data received and analyzed",
        "risk_level": risk_level,
        "predicted_diseases": risk_result.get("predicted_diseases", []),
        "optimal_conditions": risk_result.get("optimal_conditions", True),
        "summary": risk_result.get("summary", ""),
        "analysis": risk_result,
        "log_id": log_id
    }


# ─── GET LATEST SENSOR READING ──────────────────────────────
@router.get("/sensors/{farm_id}/latest")
def get_latest_reading(farm_id: str):
    """Get the latest sensor reading for a farm. NO AUTH REQUIRED"""
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
    limit: int = Query(default=50, le=200)
):
    """Get sensor reading history for a farm. NO AUTH REQUIRED"""
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
def get_risk_status(farm_id: str):
    """Get latest reading and its risk analysis. NO AUTH REQUIRED"""
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
