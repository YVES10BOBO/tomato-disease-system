from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.disease.models import DetectionCreate, DetectionStatusUpdate
from app.auth.utils import decode_token
from app.database.connection import supabase
from typing import Optional

router = APIRouter(prefix="/disease", tags=["Disease Detection"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_severity(confidence: float, disease_name: str) -> str:
    """Determine severity based on confidence score and disease type"""
    critical_diseases = ["Late Blight", "Bacterial Wilt"]
    if disease_name in critical_diseases:
        return "critical" if confidence >= 80 else "high"
    if confidence >= 90:
        return "high"
    elif confidence >= 70:
        return "medium"
    return "low"


# ─── SUBMIT DETECTION (from Raspberry Pi) ───────────────────
@router.post("/detect", status_code=201)
def submit_detection(data: DetectionCreate):
    """
    Called by Raspberry Pi after AI model detects a disease.
    Stores detection result and creates alert for farmer.
    """
    # Get zone ID from zone_code
    zone = supabase.table("farm_zones")\
        .select("id")\
        .eq("farm_id", data.farm_id)\
        .eq("zone_code", data.zone_code)\
        .execute()

    zone_id = zone.data[0]["id"] if zone.data else None

    # Get disease details from diseases table
    disease = supabase.table("diseases")\
        .select("id, severity")\
        .eq("name", data.disease_name)\
        .execute()

    disease_id = disease.data[0]["id"] if disease.data else None
    severity = get_severity(data.confidence_score, data.disease_name)

    # Save detection
    detection = supabase.table("detections").insert({
        "farm_id": data.farm_id,
        "zone_id": zone_id,
        "disease_id": disease_id,
        "zone_code": data.zone_code,
        "disease_name": data.disease_name,
        "confidence_score": data.confidence_score,
        "severity": severity,
        "image_url": data.image_url,
        "status": "active"
    }).execute()

    detection_data = detection.data[0]

    # Get farm info to find owner
    farm = supabase.table("farms")\
        .select("owner_id, name")\
        .eq("id", data.farm_id)\
        .execute()

    if farm.data:
        owner_id = farm.data[0]["owner_id"]
        farm_name = farm.data[0]["name"]

        # Get treatment recommendation
        treatment = "Monitor closely and apply appropriate fungicide."
        if disease.data:
            full_disease = supabase.table("diseases")\
                .select("treatment")\
                .eq("id", disease_id)\
                .execute()
            if full_disease.data:
                treatment = full_disease.data[0]["treatment"]

        # Create alert
        supabase.table("alerts").insert({
            "farm_id": data.farm_id,
            "user_id": owner_id,
            "detection_id": detection_data["id"],
            "alert_type": "disease",
            "title": f"Disease Detected in Zone {data.zone_code} — {farm_name}",
            "message": f"{data.disease_name} detected with {data.confidence_score:.1f}% confidence. {treatment}",
            "zone_code": data.zone_code,
            "risk_level": severity
        }).execute()

    return {
        "message": "Detection recorded",
        "detection_id": detection_data["id"],
        "disease": data.disease_name,
        "zone": data.zone_code,
        "severity": severity,
        "confidence": data.confidence_score
    }


# ─── GET ALL DETECTIONS FOR A FARM ──────────────────────────
@router.get("/{farm_id}/detections")
def get_detections(
    farm_id: str,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
    user=Depends(get_current_user)
):
    query = supabase.table("detections")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("detected_at", desc=True)\
        .limit(limit)

    if status:
        query = query.eq("status", status)

    result = query.execute()
    return {"detections": result.data, "total": len(result.data)}


# ─── GET SINGLE DETECTION ───────────────────────────────────
@router.get("/detections/{detection_id}")
def get_detection(detection_id: str, user=Depends(get_current_user)):
    result = supabase.table("detections")\
        .select("*")\
        .eq("id", detection_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Detection not found")

    detection = result.data[0]

    # Get disease details
    if detection.get("disease_id"):
        disease = supabase.table("diseases")\
            .select("*")\
            .eq("id", detection["disease_id"])\
            .execute()
        detection["disease_details"] = disease.data[0] if disease.data else None

    return detection


# ─── UPDATE DETECTION STATUS ────────────────────────────────
@router.patch("/detections/{detection_id}/status")
def update_detection_status(
    detection_id: str,
    update: DetectionStatusUpdate,
    user=Depends(get_current_user)
):
    if update.status not in ["active", "treated", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    update_data = {"status": update.status}
    if update.status == "resolved":
        from datetime import datetime, timezone
        update_data["resolved_at"] = datetime.now(timezone.utc).isoformat()

    result = supabase.table("detections")\
        .update(update_data)\
        .eq("id", detection_id)\
        .execute()

    return {"message": f"Detection marked as {update.status}", "detection": result.data[0]}


# ─── GET ACTIVE DISEASE ZONES (farm map view) ───────────────
@router.get("/{farm_id}/active-zones")
def get_active_zones(farm_id: str, user=Depends(get_current_user)):
    """Returns all zones that currently have active disease detections"""
    result = supabase.table("detections")\
        .select("zone_code, disease_name, severity, confidence_score, detected_at")\
        .eq("farm_id", farm_id)\
        .eq("status", "active")\
        .execute()

    return {
        "farm_id": farm_id,
        "affected_zones": result.data,
        "total_affected": len(result.data)
    }


# ─── GET DISEASE STATISTICS ─────────────────────────────────
@router.get("/{farm_id}/stats")
def get_disease_stats(farm_id: str, user=Depends(get_current_user)):
    all_detections = supabase.table("detections")\
        .select("disease_name, status, severity")\
        .eq("farm_id", farm_id)\
        .execute()

    data = all_detections.data
    stats = {
        "total": len(data),
        "active": len([d for d in data if d["status"] == "active"]),
        "treated": len([d for d in data if d["status"] == "treated"]),
        "resolved": len([d for d in data if d["status"] == "resolved"]),
        "by_disease": {},
        "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0}
    }

    for d in data:
        name = d["disease_name"]
        stats["by_disease"][name] = stats["by_disease"].get(name, 0) + 1
        if d["severity"] in stats["by_severity"]:
            stats["by_severity"][d["severity"]] += 1

    return stats
