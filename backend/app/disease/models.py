from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DetectionCreate(BaseModel):
    farm_id: str
    zone_code: str
    disease_name: str
    confidence_score: float
    severity: Optional[str] = "medium"
    image_url: Optional[str] = None


class DetectionStatusUpdate(BaseModel):
    status: str  # active, treated, resolved
