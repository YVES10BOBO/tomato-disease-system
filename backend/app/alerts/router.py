from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.utils import decode_token
from app.database.connection import supabase
from typing import Optional

router = APIRouter(prefix="/alerts", tags=["Alerts"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ─── GET ALL ALERTS FOR USER ────────────────────────────────
@router.get("/")
def get_my_alerts(
    is_read: Optional[bool] = Query(default=None),
    alert_type: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
    user=Depends(get_current_user)
):
    query = supabase.table("alerts")\
        .select("*")\
        .eq("user_id", user["sub"])\
        .order("sent_at", desc=True)\
        .limit(limit)

    if is_read is not None:
        query = query.eq("is_read", is_read)
    if alert_type:
        query = query.eq("alert_type", alert_type)

    result = query.execute()

    unread = supabase.table("alerts")\
        .select("id")\
        .eq("user_id", user["sub"])\
        .eq("is_read", False)\
        .execute()

    return {
        "alerts": result.data,
        "total": len(result.data),
        "unread_count": len(unread.data)
    }


# ─── MARK ALERT AS READ ─────────────────────────────────────
@router.patch("/{alert_id}/read")
def mark_as_read(alert_id: str, user=Depends(get_current_user)):
    result = supabase.table("alerts")\
        .update({"is_read": True})\
        .eq("id", alert_id)\
        .eq("user_id", user["sub"])\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert marked as read"}


# ─── MARK ALL ALERTS AS READ ────────────────────────────────
@router.patch("/read-all")
def mark_all_as_read(user=Depends(get_current_user)):
    supabase.table("alerts")\
        .update({"is_read": True})\
        .eq("user_id", user["sub"])\
        .eq("is_read", False)\
        .execute()
    return {"message": "All alerts marked as read"}


# ─── GET UNREAD COUNT ───────────────────────────────────────
@router.get("/unread-count")
def get_unread_count(user=Depends(get_current_user)):
    result = supabase.table("alerts")\
        .select("id")\
        .eq("user_id", user["sub"])\
        .eq("is_read", False)\
        .execute()
    return {"unread_count": len(result.data)}


# ─── GET FARM ALERTS ────────────────────────────────────────
@router.get("/farm/{farm_id}")
def get_farm_alerts(
    farm_id: str,
    limit: int = Query(default=20, le=100),
    user=Depends(get_current_user)
):
    result = supabase.table("alerts")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("sent_at", desc=True)\
        .limit(limit)\
        .execute()

    return {"alerts": result.data, "total": len(result.data)}


# ─── GET DAILY SUMMARY ──────────────────────────────────────
@router.get("/farm/{farm_id}/summary")
def get_daily_summary(farm_id: str, user=Depends(get_current_user)):
    from datetime import datetime, timezone, timedelta

    today = datetime.now(timezone.utc).date().isoformat()

    # Get today's detections
    detections = supabase.table("detections")\
        .select("disease_name, severity, zone_code, status")\
        .eq("farm_id", farm_id)\
        .gte("detected_at", f"{today}T00:00:00Z")\
        .execute()

    # Get today's sensor readings
    sensors = supabase.table("sensor_logs")\
        .select("temperature, humidity, soil_moisture, risk_level")\
        .eq("farm_id", farm_id)\
        .gte("recorded_at", f"{today}T00:00:00Z")\
        .execute()

    # Get today's alerts
    alerts = supabase.table("alerts")\
        .select("alert_type, risk_level, title")\
        .eq("farm_id", farm_id)\
        .gte("sent_at", f"{today}T00:00:00Z")\
        .execute()

    # Calculate averages
    avg_temp = avg_humidity = avg_soil = 0
    if sensors.data:
        avg_temp = round(sum(s["temperature"] for s in sensors.data) / len(sensors.data), 1)
        avg_humidity = round(sum(s["humidity"] for s in sensors.data) / len(sensors.data), 1)
        avg_soil = round(sum(s["soil_moisture"] for s in sensors.data) / len(sensors.data), 1)

    # Overall health
    active_detections = [d for d in detections.data if d["status"] == "active"]
    if any(d["severity"] == "critical" for d in active_detections):
        health = "CRITICAL"
    elif any(d["severity"] == "high" for d in active_detections):
        health = "HIGH RISK"
    elif active_detections:
        health = "MODERATE RISK"
    else:
        health = "HEALTHY"

    return {
        "date": today,
        "farm_id": farm_id,
        "overall_health": health,
        "detections_today": len(detections.data),
        "active_diseases": len(active_detections),
        "alerts_today": len(alerts.data),
        "sensor_averages": {
            "temperature": avg_temp,
            "humidity": avg_humidity,
            "soil_moisture": avg_soil
        },
        "scans_today": len(sensors.data)
    }
