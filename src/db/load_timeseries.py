# load_timeseries.py
from db.database import init_db, load_time_series

if __name__ == "__main__":
    init_db()  # ensures table exists

    csv_path = "x"
    load_time_series(csv_path)
    print("✅ Time series data loaded.")

    