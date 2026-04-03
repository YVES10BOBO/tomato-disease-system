from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SensorData(BaseModel):
    farm_id: str
    temperature: float
    humidity: float
    soil_moisture: float


class SensorLogResponse(BaseModel):
    id: str
    farm_id: str
    temperature: float
    humidity: float
    soil_moisture: float
    risk_level: str
    recorded_at: datetime
