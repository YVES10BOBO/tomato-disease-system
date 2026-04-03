from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FarmCreate(BaseModel):
    name: str
    location: str
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    size_hectares: Optional[float] = None


class FarmResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    location: str
    district: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    size_hectares: Optional[float]
    total_zones: int
    is_active: bool
    created_at: datetime


class FarmSettingsUpdate(BaseModel):
    scan_interval_minutes: Optional[int] = 30
    night_mode_start: Optional[str] = "20:00:00"
    night_mode_end: Optional[str] = "06:00:00"
    night_scan_interval_minutes: Optional[int] = 60
    morning_report_time: Optional[str] = "06:00:00"
    evening_report_time: Optional[str] = "20:00:00"
    alert_notifications: Optional[bool] = True
    warning_notifications: Optional[bool] = True
    daily_summary: Optional[bool] = True
    risk_sensitivity: Optional[str] = "medium"
    auto_override_enabled: Optional[bool] = True
