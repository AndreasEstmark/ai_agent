import os
import asyncio
import random
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncAzureOpenAI

from schemas.timeseries import WorstInterferenceOutput
from tools.timeseries import register_timeseries_tools
import logfire
from db.database import engine

# -------------------------------
# Logfire instrumentation
# -------------------------------
logfire.configure()

if not getattr(logfire, "_instrumented", False):
    logfire.instrument_pydantic_ai()
    logfire.instrument_openai()
    logfire.instrument_sqlalchemy(engine=engine)

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Azure client setup
# -------------------------------
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

# -------------------------------
# Time series agent
# -------------------------------
timeseries_agent = Agent(
    model=model,
    output_type=WorstInterferenceOutput,
)

register_timeseries_tools(timeseries_agent)

@timeseries_agent.system_prompt
def timeseries_sys(ctx: RunContext) -> str:
    return """
    You are a time series analysis assistant.
    You have access to tools such as `get_worst_interference`.
    
    Rules:
    1. Use tools only when necessary to fetch missing data.
    2. Do not call the same tool multiple times for the same user question.
    3. If the user asks about available tools, list them instead of calling them.
    4. Provide concise answers and use structured JSON when appropriate.
    """

# -------------------------------
# Retry/backoff for 429 errors
# -------------------------------
async def run_with_retry(coro_func, *args, max_retries=5, initial_backoff=1, **kwargs):
    backoff = initial_backoff
    for attempt in range(max_retries):
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            if status_code == 429:
                print(f"[retry] Rate limit hit, backing off {backoff}s (attempt {attempt+1})")
                await asyncio.sleep(backoff + random.uniform(0, 0.5))
                backoff *= 2
            else:
                raise
    raise RuntimeError("Max retries exceeded")

# -------------------------------
# Main loop
# -------------------------------
async def main():
    print("💬 TimeSeries Agent (type 'exit' to quit)\n")

    called_tools_per_query = set()  # track tools per query

    while True:
        query = input("> ")
        if query.lower() in {"exit", "quit"}:
            break

        try:
            # Run the agent with retry logic
            result = await run_with_retry(timeseries_agent.run, query)

            # Track tools used (prevent multiple calls)
            if hasattr(result, "tools_used"):
                called_tools_per_query.update(result.tools_used)

            # 1️⃣ Structured output
            print("🔹 Structured Output (Pydantic):")
            print(result.output.model_dump_json(indent=2))

            # 2️⃣ Raw model output
            print("\n🔹 Model Raw Output:")
            # Optional raw text (unvalidated)
            raw_text = getattr(result, "raw_text", None)
            if raw_text:
                print(raw_text)
            else:
                print("[No raw output available]")

        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
