from typing import Optional, Any, Dict
from datetime import date
from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import SQLModel, Field

class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    make: str
    year: int
    last_service_date: date
    mileage: int
    issues: Dict[str, Any] = Field(
    default_factory=dict,
    sa_column=Column(JSON)
)


class TimeSeries(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hex: str = Field(index=True)  
    good_aircraft: int
    bad_aircraft: int
    total: int
    interference_ratio: float
    lat: float
    lon: float