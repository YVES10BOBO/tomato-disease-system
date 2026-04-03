from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.models import UserRegister, UserLogin, TokenResponse, UserResponse
from app.auth.utils import hash_password, verify_password, create_access_token, decode_token
from app.database.connection import supabase
from pydantic import BaseModel
from typing import Optional

class ProfileUpdate(BaseModel):
    full_name: str
    phone: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    # Check if email already exists
    existing = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone already exists
    existing_phone = supabase.table("users").select("id").eq("phone", user.phone).execute()
    if existing_phone.data:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create user
    new_user = supabase.table("users").insert({
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "password_hash": hash_password(user.password),
        "role": user.role
    }).execute()

    created = new_user.data[0]

    # Generate token
    token = create_access_token({"sub": created["id"], "role": created["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": created
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    # Find user by email
    result = supabase.table("users").select("*").eq("email", credentials.email).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check active
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Generate token
    token = create_access_token({"sub": user["id"], "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    result = supabase.table("users").select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data[0]


@router.put("/profile")
def update_profile(data: ProfileUpdate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    result = supabase.table("users").update({
        "full_name": data.full_name,
        "phone": data.phone,
    }).eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated", "user": result.data[0]}


@router.put("/change-password")
def change_password(data: PasswordChange, credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    user = result.data[0]
    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    supabase.table("users").update({
        "password_hash": hash_password(data.new_password)
    }).eq("id", user_id).execute()
    return {"message": "Password changed successfully"}
