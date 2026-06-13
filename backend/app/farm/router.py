from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.farm.models import FarmCreate, FarmResponse, FarmSettingsUpdate
from app.auth.utils import decode_token
from app.database.connection import supabase
from datetime import datetime, timedelta, timezone, time as dtime

router = APIRouter(prefix="/farms", tags=["Farms"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def generate_zones(farm_id: str):
    """Auto-generate 16 grid zones A1-D4 for a farm"""
    zones = []
    for row in ["A", "B", "C", "D"]:
        for col in range(1, 5):
            zones.append({
                "farm_id": farm_id,
                "zone_code": f"{row}{col}",
                "row_label": row,
                "col_number": col
            })
    supabase.table("farm_zones").insert(zones).execute()


def create_default_settings(farm_id: str):
    """Create default scan/notification settings for a farm"""
    supabase.table("farm_settings").insert({
        "farm_id": farm_id
    }).execute()


# ─── CREATE FARM ────────────────────────────────────────────
@router.post("/", status_code=201)
def create_farm(farm: FarmCreate, user=Depends(get_current_user)):
    result = supabase.table("farms").insert({
        "owner_id": user["sub"],
        "name": farm.name,
        "location": farm.location,
        "district": farm.district,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "size_hectares": farm.size_hectares
    }).execute()

    created_farm = result.data[0]
    farm_id = created_farm["id"]

    # Auto-generate zones and default settings
    generate_zones(farm_id)
    create_default_settings(farm_id)

    return {
        "message": "Farm created successfully",
        "farm": created_farm
    }


# ─── GET ALL MY FARMS ───────────────────────────────────────
@router.get("/")
def get_my_farms(user=Depends(get_current_user)):
    result = supabase.table("farms")\
        .select("*")\
        .eq("owner_id", user["sub"])\
        .eq("is_active", True)\
        .execute()
    return {"farms": result.data, "total": len(result.data)}


# ─── GET FARM BY ID ─────────────────────────────────────────
@router.get("/{farm_id}")
def get_farm(farm_id: str, user=Depends(get_current_user)):
    result = supabase.table("farms")\
        .select("*")\
        .eq("id", farm_id)\
        .eq("owner_id", user["sub"])\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Farm not found")
    return result.data[0]


# ─── GET FARM ZONES ─────────────────────────────────────────
@router.get("/{farm_id}/zones")
def get_farm_zones(farm_id: str, user=Depends(get_current_user)):
    result = supabase.table("farm_zones")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .order("zone_code")\
        .execute()
    return {"zones": result.data, "total": len(result.data)}


# ─── GET FARM SETTINGS ──────────────────────────────────────
@router.get("/{farm_id}/settings")
def get_farm_settings(farm_id: str, user=Depends(get_current_user)):
    result = supabase.table("farm_settings")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Settings not found")
    return result.data[0]


# ─── UPDATE FARM SETTINGS ───────────────────────────────────
@router.put("/{farm_id}/settings")
def update_farm_settings(farm_id: str, settings: FarmSettingsUpdate, user=Depends(get_current_user)):
    update_data = {k: v for k, v in settings.model_dump().items() if v is not None}

    result = supabase.table("farm_settings")\
        .update(update_data)\
        .eq("farm_id", farm_id)\
        .execute()

    return {"message": "Settings updated successfully", "settings": result.data[0]}


# ─── DELETE FARM ────────────────────────────────────────────
@router.delete("/{farm_id}")
def delete_farm(farm_id: str, user=Depends(get_current_user)):
    supabase.table("farms")\
        .update({"is_active": False})\
        .eq("id", farm_id)\
        .eq("owner_id", user["sub"])\
        .execute()
    return {"message": "Farm deactivated successfully"}


# ─── ADAPTIVE CAMERA SCAN INTERVAL ──────────────────────────
# Risk level -> recommended scan interval (minutes)
RISK_INTERVAL_MINUTES = {
    "low": 30,
    "medium": 15,
    "high": 10,
    "critical": 5,
}


def _is_night(now: datetime, start: str, end: str) -> bool:
    """True if current local time falls inside the night-mode window.
    Window may wrap past midnight (e.g. 20:00 -> 06:00)."""
    def parse(t: str) -> dtime:
        h, m, *rest = (t or "00:00:00").split(":")
        return dtime(int(h), int(m))

    cur = now.time()
    s, e = parse(start), parse(end)
    if s <= e:
        return s <= cur <= e
    # wraps midnight
    return cur >= s or cur <= e


@router.get("/{farm_id}/scan-interval")
def get_scan_interval(farm_id: str, user=Depends(get_current_user)):
    """
    Called by the Raspberry Pi camera before each capture cycle.
    Returns the recommended scan interval (minutes), adapting to the
    farm's current environmental risk level and night-mode settings.

    Logic:
      - If a disease was detected on this farm in the last 24h -> CRITICAL (5 min)
      - Otherwise use the latest IoT sensor risk level:
            low=30, medium=15, high=10, critical=5
      - Night mode overrides to the farm's night interval (default 60 min)
      - If auto-override is disabled, return the farmer's fixed manual interval
    """
    # 1. Load farm settings (manual interval, night mode, auto override)
    settings_res = supabase.table("farm_settings")\
        .select("*")\
        .eq("farm_id", farm_id)\
        .execute()
    settings = settings_res.data[0] if settings_res.data else {}

    manual_interval = settings.get("scan_interval_minutes", 30)
    night_interval = settings.get("night_scan_interval_minutes", 60)
    night_start = settings.get("night_mode_start", "20:00:00")
    night_end = settings.get("night_mode_end", "06:00:00")
    auto_override = settings.get("auto_override_enabled", True)

    now = datetime.now()

    # 2. If farmer disabled adaptive scanning, honour their fixed interval
    if not auto_override:
        return {
            "farm_id": farm_id,
            "risk_level": "manual",
            "scan_interval_minutes": manual_interval,
            "reason": "Auto-override disabled — using farmer's fixed interval",
            "night_mode": False,
        }

    # 3. Night mode takes priority — scan less often at night
    if _is_night(now, night_start, night_end):
        return {
            "farm_id": farm_id,
            "risk_level": "night",
            "scan_interval_minutes": night_interval,
            "reason": "Night mode active — reduced scan frequency",
            "night_mode": True,
        }

    # 4. Active disease in last 24h -> Critical (scan most often)
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    recent = supabase.table("detections")\
        .select("id")\
        .eq("farm_id", farm_id)\
        .eq("status", "active")\
        .gte("detected_at", since)\
        .limit(1)\
        .execute()
    if recent.data:
        return {
            "farm_id": farm_id,
            "risk_level": "critical",
            "scan_interval_minutes": RISK_INTERVAL_MINUTES["critical"],
            "reason": "Active disease detected in the last 24 hours",
            "night_mode": False,
        }

    # 5. Otherwise base interval on the latest sensor risk level
    latest = supabase.table("sensor_logs")\
        .select("risk_level, recorded_at")\
        .eq("farm_id", farm_id)\
        .order("recorded_at", desc=True)\
        .limit(1)\
        .execute()

    risk_level = latest.data[0]["risk_level"] if latest.data else "low"
    interval = RISK_INTERVAL_MINUTES.get(risk_level, 30)

    return {
        "farm_id": farm_id,
        "risk_level": risk_level,
        "scan_interval_minutes": interval,
        "reason": f"Based on latest environmental risk level: {risk_level}",
        "night_mode": False,
    }
