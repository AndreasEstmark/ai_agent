from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from .models import Car

DB_PATH = Path("storage/database.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)

def init_db():
    SQLModel.metadata.create_all(engine)

def seed():
    from datetime import date
    rows = [
        Car(id=1, make="Volvo", year=2018, last_service_date=date.fromisoformat("2023-06-15"),
            mileage=45000, issues={"engine": "none", "tires": "good"}),
        Car(id=2, make="Saab", year=2020, last_service_date=date.fromisoformat("2023-08-20"),
            mileage=30000, issues={"engine": "big oil leak", "tires": "bad"}),
    ]
    with Session(engine) as s:
        for r in rows:
            s.merge(r)  # insert or update
        s.commit()
