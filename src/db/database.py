from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from .models import Car, TimeSeries
import pandas as pd


# ----------------------------
# Database setup
# ----------------------------

DB_PATH = Path("storage/database.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


# ----------------------------
# Seed functions (for testing/demo only)
# ----------------------------

def seed() -> None:
    """Insert demo cars into the Car table."""
    from datetime import date

    rows = [
        Car(
            id=1,
            make="Volvo",
            year=2018,
            last_service_date=date.fromisoformat("2023-06-15"),
            mileage=45000,
            issues={"engine": "none", "tires": "good"},
        ),
        Car(
            id=2,
            make="Saab",
            year=2020,
            last_service_date=date.fromisoformat("2023-08-20"),
            mileage=30000,
            issues={"engine": "big oil leak", "tires": "bad"},
        ),
    ]

    with Session(engine) as session:
        for r in rows:
            session.merge(r)  # insert or update
        session.commit()

    print("✅ Car table seeded with demo rows.")


# ----------------------------
# Data loading functions
# ----------------------------

def load_time_series(csv_path: str) -> None:
    """Load GPS interference CSV into TimeSeries table."""
    df = pd.read_csv(csv_path)

    rows = [
        TimeSeries(
            hex=row["hex"],
            good_aircraft=int(row["good_aircraft"]),
            bad_aircraft=int(row["bad_aircraft"]),
            total=int(row["total"]),
            interference_ratio=float(row["interference_ratio"]),
            lat=float(row["lat"]),
            lon=float(row["lon"]),
        )
        for _, row in df.iterrows()
    ]

    with Session(engine) as session:
        session.bulk_save_objects(rows)  # efficient batch insert
        session.commit()

    print(f"✅ Inserted {len(rows)} rows from {csv_path} into TimeSeries table.")
