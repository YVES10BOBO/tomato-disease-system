from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.disease.models import DetectionCreate, DetectionStatusUpdate
from app.disease.ai_model import load_model, predict_disease, is_plant_leaf
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


# ─── AI PREDICT (from Mobile Scan screen) ───────────────────
@router.post("/predict", status_code=200)
async def predict(
    file: UploadFile = File(...),
    farm_id: str = Form(...),
    zone_code: str = Form(...),
    user=Depends(get_current_user)
):
    """
    Called by mobile Scan screen.
    Receives a leaf photo, runs AI model, saves detection, returns result.
    """
    # Check model is loaded
    if not load_model():
        raise HTTPException(
            status_code=503,
            detail="AI model not yet deployed. Please train the model first."
        )

    # Read image bytes
    image_bytes = await file.read()

    # Run AI prediction
    try:
        result = predict_disease(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Step 1: Check if image is actually a plant/leaf
    if not is_plant_leaf(image_bytes):
        return {
            "disease_name": "Unknown",
            "confidence_score": 0.0,
            "is_healthy": False,
            "severity": "none",
            "treatment": "Please take a clear photo of a tomato leaf and try again.",
            "description": "Image does not appear to be a plant or leaf.",
            "saved": False
        }

    # Step 2: Reject low-confidence disease predictions
    if result["confidence_score"] < 70.0:
        return {
            "disease_name": "Unknown",
            "confidence_score": result["confidence_score"],
            "is_healthy": False,
            "severity": "none",
            "treatment": "Please take a clearer photo of a tomato leaf and try again.",
            "description": "Could not determine disease with enough confidence.",
            "saved": False
        }

    # If healthy, return without saving to DB
    if result["is_healthy"]:
        return {
            "disease_name": "Healthy",
            "confidence_score": result["confidence_score"],
            "is_healthy": True,
            "severity": "none",
            "treatment": result["treatment"],
            "description": result["description"],
            "saved": False
        }

    # Save detection to database
    severity = get_severity(result["confidence_score"], result["disease_name"])

    # Get zone ID
    zone = supabase.table("farm_zones")\
        .select("id")\
        .eq("farm_id", farm_id)\
        .eq("zone_code", zone_code)\
        .execute()
    zone_id = zone.data[0]["id"] if zone.data else None

    # Get disease ID
    disease = supabase.table("diseases")\
        .select("id")\
        .eq("name", result["disease_name"])\
        .execute()
    disease_id = disease.data[0]["id"] if disease.data else None

    detection = supabase.table("detections").insert({
        "farm_id": farm_id,
        "zone_id": zone_id,
        "disease_id": disease_id,
        "zone_code": zone_code,
        "disease_name": result["disease_name"],
        "confidence_score": result["confidence_score"],
        "severity": severity,
        "status": "active"
    }).execute()

    detection_id = detection.data[0]["id"] if detection.data else None

    # Create alert for farmer
    farm = supabase.table("farms").select("owner_id, name").eq("id", farm_id).execute()
    if farm.data:
        owner_id = farm.data[0]["owner_id"]
        farm_name = farm.data[0]["name"]
        supabase.table("alerts").insert({
            "farm_id": farm_id,
            "user_id": owner_id,
            "detection_id": detection_id,
            "alert_type": "disease",
            "title": f"Disease Detected in Zone {zone_code} — {farm_name}",
            "message": f"{result['disease_name']} detected with {result['confidence_score']:.1f}% confidence. {result['treatment']}",
            "zone_code": zone_code,
            "risk_level": severity
        }).execute()

    return {
        "disease_name": result["disease_name"],
        "confidence_score": result["confidence_score"],
        "is_healthy": False,
        "severity": severity,
        "treatment": result["treatment"],
        "description": result["description"],
        "detection_id": detection_id,
        "saved": True
    }


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
