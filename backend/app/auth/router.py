from fastapi import APIRouter, HTTPException, status
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


@router.get("/me")
def get_current_user():
    # For development: return a default user without auth
    # In production, add back: credentials: HTTPAuthorizationCredentials = Depends(security)
    return {
        "id": "dev-user",
        "email": "dev@tomato.local",
        "full_name": "Development User",
        "role": "farmer",
        "is_active": True
    }


@router.put("/profile")
def update_profile(data: ProfileUpdate):
    # For development: accept profile updates without auth
    # In production, add back: credentials: HTTPAuthorizationCredentials = Depends(security)
    return {"message": "Profile updated (development mode)", "user": {"full_name": data.full_name, "phone": data.phone}}


@router.put("/change-password")
def change_password(data: PasswordChange):
    # For development: accept password changes without auth
    # In production, add back: credentials: HTTPAuthorizationCredentials = Depends(security)
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    return {"message": "Password changed successfully (development mode)"}
