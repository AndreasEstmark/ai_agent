import asyncio
import os
from db.database import init_db, seed, engine
from schemas import MaintenanceDependency, MaintenanceOutput
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI
from tools.cars import register_tools


import json
import logfire

# configure logfire
logfire.configure()
logfire.instrument_pydantic_ai()
logfire.instrument_openai()  # instrument all OpenAI clients globally
logfire.instrument_sqlalchemy(engine=engine)


load_dotenv()  # will load .env from repo root if present


client = AsyncAzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.getenv("API_KEY"))

model = OpenAIChatModel(
    'gpt-5-mini',
    provider=OpenAIProvider(openai_client=client),
)

maintenance_agent = Agent(
    model=model,
    deps_type=MaintenanceDependency,
    output_type=MaintenanceOutput,
)

register_tools(maintenance_agent)


GENERIC_OUTPUT_REQ = "Return a well-structured result per the agent's output schema."

@maintenance_agent.system_prompt
def maintenance_sys(ctx: RunContext[MaintenanceDependency]) -> str:
    """
    Generates a robust system prompt for the maintenance agent.
    """

    deps_json = json.dumps(ctx.deps.model_dump(), ensure_ascii=False, indent=2)

    return f"""
        You are a professional car mechanic AI assistant.

        Your primary task is to provide a maintenance recommendation for a car.
        Explain your reasoning in a concise step-by-step manner before giving a recommendation.

        You must always return a JSON object matching the MaintenanceOutput schema:

        {{
            "recommendation": "<message to car owner>",
            "urgency": "<integer 1-10>"
        }}

        Instructions:
        1. If any car information is missing in the context, always use the tool `get_car_info` to fetch it.
        2. Do not guess car data; rely on tools whenever the context is incomplete.
        3. Be concise but provide clear reasoning for the urgency level.
        4. Use the provided 'car_id' in the context to fetch car data.
        5. Validate that 'urgency' is an integer between 1 (low) and 10 (high).
        6. If the car has no reported issues, note this explicitly in the recommendation.
        7. Format the output strictly as JSON; do not include additional text outside the JSON object.

        Context (preloaded info):
        {deps_json}

        Example output:
        {{
            "recommendation": "Car ID 1 — 2018 Volvo, 45,000 miles. Last serviced on 2023-06-15. No issues reported. Schedule routine service in 3 months.",
            "urgency": 4
        }}

        Always follow this structure and these rules.
        """

async def handler(ctx, event):
    # ctx is the RunContext[MaintenanceDependency] for this run
    # event is the stream event (ToolCallEvent, ModelResponseEvent, etc.)
    print("RunContext deps:", ctx.deps)
    print("Event:", event)

async def main():
    # Create tables + add rows before any queries happen
    init_db()
    seed()

    print("DB file:", engine.url.database)  # sanity check which file you’re using

    car_id = 2
    deps = MaintenanceDependency(car_id=car_id)

    prompt =  f"Give me info for car {car_id} and suggest maintenance if needed."

    result = await maintenance_agent.run(prompt, deps=deps

)
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())