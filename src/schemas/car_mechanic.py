# schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

# Car maintenance domain

class MaintenanceDependency(BaseModel):
    car_id: int

class MaintenanceOutput(BaseModel):
    recommendation: str
    urgency: int = Field(..., ge=1, le=10)

