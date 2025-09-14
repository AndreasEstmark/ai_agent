from typing import Any
from sqlmodel import Session
from pydantic_ai import Agent
from db.database import engine
from db.models import Car
from pydantic_ai import RunContext

from schemas import MaintenanceDependency


def get_car_info(ctx: RunContext[MaintenanceDependency]) -> dict[str, Any]:
    """
    Fetch car info from the database using the current run's dependencies.

    Args:
        ctx: The current RunContext, containing MaintenanceDependency

    Returns:
        Dictionary of car fields (id, make, year, mileage, last_service_date, issues)
    """
    car_id = ctx.deps.car_id
    with Session(engine) as session:
        car = session.get(Car, car_id)
        return car.model_dump() if car else {}
def register_tools(agent):
    """
    Attach tools to a given agent.
    Use tool_with_context to allow access to RunContext.
    """
    agent.tool(get_car_info)