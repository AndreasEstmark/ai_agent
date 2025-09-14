# src/schemas.py
from pydantic import BaseModel, Field
from typing import Any
from db.models import Car


class MaintenanceDependency(BaseModel):
    """Dependencies for the maintenance agent"""
    car_id: int
    car: Car | None = None

class MaintenanceOutput(BaseModel):
    """Structured output from the maintenance agent"""
    recommendation: str = Field(description="Message to the car owner about maintenance")
    urgency: int = Field(description="Urgency level from 1 (low) to 10 (high)")