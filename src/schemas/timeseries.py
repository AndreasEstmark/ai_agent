from pydantic import BaseModel, Field

from typing import List
# Interference domain

class InterferenceRow(BaseModel):
    hex: str
    good_aircraft: int
    bad_aircraft: int
    total: int
    interference_ratio: float = Field(..., ge=0.0, le=1.0)
    lat: float
    lon: float

class WorstInterferenceOutput(BaseModel):
    rows: List[InterferenceRow]
    summary: str
