import asyncio
from dataclasses import dataclass
from typing import Any
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI

import json

load_dotenv()  # will load .env from repo root if present

GENERIC_ROLE = "You are a domain expert. Use the provided JSON context faithfully."
GENERIC_OUTPUT_REQ = "Return a well-structured result per the agent's output schema."

client = AsyncAzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.getenv("API_KEY"))

model = OpenAIChatModel(
    'gpt-5-mini',
    provider=OpenAIProvider(openai_client=client),
)

# Mock database

@dataclass
class Car:
    id: int
    make:str
    year: int
    last_service_date: str
    mileage: int
    issues: dict[str, Any]

CARS_DB = {
    1: Car(id=1, make = "Volvo", year=2018, last_service_date="2023-06-15", mileage=45000, issues={"engine": "none", "tires": "good"}),
    2: Car(id=2,make = "Saab", year=2020, last_service_date="2023-08-20", mileage=30000, issues={"engine": "big oil leak", "tires": "bad"})

}

class DatabaseConn:

    def __init__(self):
        pass

    async def car_name(self, car_id: int) -> str:
        car = CARS_DB.get(car_id)
        return car.make if car else "Unknown Make"
    
    async def car_issues(self, car_id: int) -> dict[str, Any]:
        car = CARS_DB.get(car_id)
        return car.issues if car else {}

    

class MaintenanceDependency(BaseModel):
    car_id: int
    car_make: str | None = None
    car_issues: dict[str, Any] = Field(default_factory=dict)

class MaintenanceOutput(BaseModel):
    recommendation: str = Field(description="Message to the car owner about maintenance")
    urgency: int = Field(description="Urgency level from 1 (low) to 10 (high)")
                                          

maintenance_agent = Agent(
    model=model,
    deps_type=MaintenanceDependency,
    output_type=MaintenanceOutput,
)

@maintenance_agent.system_prompt
def maintenance_sys(ctx: RunContext[MaintenanceDependency]) -> str:
    deps_json = json.dumps(ctx.deps.model_dump(), ensure_ascii=False, indent=2)
    return f"{GENERIC_ROLE}\n\nContext:\n{deps_json}\n\n{GENERIC_OUTPUT_REQ}"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

async def main() -> None:
    db = DatabaseConn()
    car_id = 1
    issues = await db.car_issues(car_id)
    make = await db.car_name(car_id)

    deps = MaintenanceDependency(car_id=car_id, car_make=make, car_issues=issues)

    result = await maintenance_agent.run(
    "What maintenance does my car need?",
    deps=deps)         
    print(result.output)
                  
if __name__ == "__main__":
    asyncio.run(main())

                                                                                                                                                                                                                 