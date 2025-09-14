import asyncio
import os
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI
from pydantic_ai.tools import tool
import httpx
import json

# -------------------
# Setup
# -------------------

load_dotenv()

client = AsyncAzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.getenv("API_KEY"),
)

model = OpenAIChatModel(
    "gpt-5-mini",
    provider=OpenAIProvider(openai_client=client),
)

# -------------------
# Mock Databases
# -------------------

@dataclass
class Car:
    id: int
    make: str
    year: int
    last_service_date: str
    mileage: int
    issues: dict[str, Any]

@dataclass
class Truck:
    id: int
    make: str
    capacity_tons: int
    mileage: int
    issues: dict[str, Any]

CARS_DB = {
    1: Car(id=1, make="Volvo", year=2018, last_service_date="2023-06-15", mileage=45000,
           issues={"engine": "none", "tires": "good"}),
    2: Car(id=2, make="Saab", year=2020, last_service_date="2023-08-20", mileage=30000,
           issues={"engine": "big oil leak", "tires": "bad"}),
}

TRUCKS_DB = {
    1: Truck(id=1, make="Scania", capacity_tons=20, mileage=120000,
             issues={"brakes": "worn", "engine": "oil leak"}),
    2: Truck(id=2, make="MAN", capacity_tons=15, mileage=95000,
             issues={"transmission": "slipping", "tires": "bald"}),
}

# -------------------
# Database Access
# -------------------

class DatabaseConn:
    async def car_info(self, car_id: int) -> dict[str, Any]:
        car = CARS_DB.get(car_id)
        return car.__dict__ if car else {}

    async def truck_info(self, truck_id: int) -> dict[str, Any]:
        truck = TRUCKS_DB.get(truck_id)
        return truck.__dict__ if truck else {}

db = DatabaseConn()

# -------------------
# Shared Structured Output
# -------------------

class MaintenanceOutput(BaseModel):
    recommendation: str = Field(description="Maintenance advice for the vehicle")
    urgency: int = Field(description="Urgency level from 1 (low) to 10 (high)")

# -------------------
# Car Mechanic Agent
# -------------------

car_agent = Agent(model=model, output_type=MaintenanceOutput)

@tool(car_agent)
async def get_car_info(car_id: int) -> dict[str, Any]:
    """Fetch information about a car by ID."""
    return await db.car_info(car_id)

@car_agent.system_prompt
def car_sys(ctx: RunContext[None]) -> str:
    return "You are a car mechanic. Use the get_car_info tool if needed. Return structured maintenance advice."

# -------------------
# Truck Mechanic Agent
# -------------------

truck_agent = Agent(model=model, output_type=MaintenanceOutput)

@tool(truck_agent)
async def get_truck_info(truck_id: int) -> dict[str, Any]:
    """Fetch information about a truck by ID."""
    return await db.truck_info(truck_id)

@truck_agent.system_prompt
def truck_sys(ctx: RunContext[None]) -> str:
    return "You are a truck mechanic. Use the get_truck_info tool if needed. Return structured maintenance advice."

# -------------------
# Weather Agent
# -------------------

class WeatherOutput(BaseModel):
    city: str
    temp_c: float
    condition: str

weather_agent = Agent(model=model, output_type=WeatherOutput)

@tool(weather_agent)
async def get_temperature(city: str) -> dict[str, Any]:
    """Get the current temperature in Celsius for a city."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": os.getenv("WEATHER_API_KEY"), "units": "metric"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return {"temp_c": data["main"]["temp"], "condition": data["weather"][0]["description"]}

@weather_agent.system_prompt
def weather_sys(ctx: RunContext[None]) -> str:
    return "You are a weather expert. Use get_temperature to fetch weather. Return structured weather data."

# -------------------
# Router Agent
# -------------------

class RouterOutput(BaseModel):
    target: str = Field(description="Which agent to call: 'car', 'truck', or 'weather'")

router_agent = Agent(model=model, output_type=RouterOutput)

@router_agent.system_prompt
def router_sys(ctx: RunContext[None]) -> str:
    return (
        "You are a router. Decide whether the user query is about a car, a truck, or weather. "
        "Return only one of: 'car', 'truck', or 'weather'."
    )

# -------------------
# Orchestration
# -------------------

async def main() -> None:
    query = "My truck with ID 1 is acting up. Can you check it?"

    route = await router_agent.run(query)
    print("Router chose:", route.output)

    if route.output.target == "car":
        result = await car_agent.run(query)
    elif route.output.target == "truck":
        result = await truck_agent.run(query)
    else:
        result = await weather_agent.run(query)

    print("Final Result:", result.output)

if __name__ == "__main__":
    asyncio.run(main())
