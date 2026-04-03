from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.utils import decode_token, hash_password
from app.database.connection import supabase
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()


# ─── HELPERS ────────────────────────────────────────────────
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Only allows admin role to access these endpoints"""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


# ─── MODELS ─────────────────────────────────────────────────
class CreateAdminUser(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    role: Optional[str] = "admin"


class UpdateUserRole(BaseModel):
    role: str


# ─── GET ALL USERS ───────────────────────────────────────────
@router.get("/users")
def get_all_users(admin=Depends(get_current_admin)):
    """Admin: get all users in the system"""
    result = supabase.table("users")\
        .select("id, full_name, email, phone, role, is_active, created_at")\
        .order("created_at", desc=True)\
        .execute()
    return {
        "users": result.data,
        "total": len(result.data)
    }


# ─── GET USER BY ID ──────────────────────────────────────────
@router.get("/users/{user_id}")
def get_user(user_id: str, admin=Depends(get_current_admin)):
    result = supabase.table("users")\
        .select("id, full_name, email, phone, role, is_active, created_at")\
        .eq("id", user_id)\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]


# ─── CREATE ADMIN USER ───────────────────────────────────────
@router.post("/users", status_code=201)
def create_admin_user(data: CreateAdminUser, admin=Depends(get_current_admin)):
    """Admin: create a new user with any role including admin"""
    # Check email exists
    existing = supabase.table("users").select("id").eq("email", data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    allowed_roles = ["admin", "farmer", "agronomist"]
    if data.role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")

    new_user = supabase.table("users").insert({
        "full_name": data.full_name,
        "email": data.email,
        "phone": data.phone,
        "password_hash": hash_password(data.password),
        "role": data.role,
        "is_active": True
    }).execute()

    created = new_user.data[0]
    return {
        "message": f"{data.role.capitalize()} account created successfully",
        "user": {
            "id": created["id"],
            "full_name": created["full_name"],
            "email": created["email"],
            "role": created["role"]
        }
    }


# ─── DEACTIVATE USER ─────────────────────────────────────────
@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str, admin=Depends(get_current_admin)):
    """Admin: block a user from logging in"""
    # Prevent admin from deactivating themselves
    if user_id == admin.get("sub"):
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    result = supabase.table("users")\
        .update({"is_active": False})\
        .eq("id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated successfully"}


# ─── REACTIVATE USER ─────────────────────────────────────────
@router.put("/users/{user_id}/reactivate")
def reactivate_user(user_id: str, admin=Depends(get_current_admin)):
    """Admin: restore a deactivated user"""
    result = supabase.table("users")\
        .update({"is_active": True})\
        .eq("id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User reactivated successfully"}


# ─── CHANGE USER ROLE ────────────────────────────────────────
@router.put("/users/{user_id}/role")
def change_user_role(user_id: str, data: UpdateUserRole, admin=Depends(get_current_admin)):
    """Admin: change a user's role"""
    allowed_roles = ["admin", "farmer", "agronomist"]
    if data.role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")

    result = supabase.table("users")\
        .update({"role": data.role})\
        .eq("id", user_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User role changed to {data.role}"}


# ─── DELETE USER ─────────────────────────────────────────────
@router.delete("/users/{user_id}")
def delete_user(user_id: str, admin=Depends(get_current_admin)):
    """Admin: permanently delete a user"""
    if user_id == admin.get("sub"):
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    result = supabase.table("users")\
        .delete()\
        .eq("id", user_id)\
        .execute()

    return {"message": "User deleted permanently"}


# ─── SYSTEM STATS ────────────────────────────────────────────
@router.get("/stats")
def get_system_stats(admin=Depends(get_current_admin)):
    """Admin: overall system statistics"""
    users = supabase.table("users").select("id, role, is_active").execute()
    farms = supabase.table("farms").select("id").execute()
    detections = supabase.table("disease_detections").select("id, status").execute()
    alerts = supabase.table("alerts").select("id, is_read").execute()

    all_users = users.data or []
    return {
        "total_users": len(all_users),
        "total_farmers": len([u for u in all_users if u["role"] == "farmer"]),
        "total_agronomists": len([u for u in all_users if u["role"] == "agronomist"]),
        "total_admins": len([u for u in all_users if u["role"] == "admin"]),
        "active_users": len([u for u in all_users if u["is_active"]]),
        "inactive_users": len([u for u in all_users if not u["is_active"]]),
        "total_farms": len(farms.data or []),
        "total_detections": len(detections.data or []),
        "active_detections": len([d for d in (detections.data or []) if d["status"] == "active"]),
        "total_alerts": len(alerts.data or []),
        "unread_alerts": len([a for a in (alerts.data or []) if not a["is_read"]]),
    }
