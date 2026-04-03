from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.farm.models import FarmCreate, FarmResponse, FarmSettingsUpdate
from app.auth.utils import decode_token
from app.database.connection import supabase

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
