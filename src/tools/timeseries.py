from sqlmodel import Session, select, desc
from pydantic_ai import RunContext
from db.database import engine
from db.models import TimeSeries
from schemas.timeseries import WorstInterferenceOutput, InterferenceRow


def get_worst_interference(ctx: RunContext) -> WorstInterferenceOutput:
    """Fetch the 10 rows with the worst interference ratio."""
    with Session(engine) as session:
        statement = select(TimeSeries).order_by(desc(TimeSeries.interference_ratio)).limit(10)
        rows = session.exec(statement).all()

    return WorstInterferenceOutput(
    summary=f"Top {len(rows)} worst interference locations",
    rows=[InterferenceRow(**r.model_dump()) for r in rows]
)


def register_timeseries_tools(agent):
    """Attach time series analysis tools to the given agent."""
    agent.tool(get_worst_interference)
