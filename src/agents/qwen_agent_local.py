
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

ollama_model = OpenAIModel(
    model_name="qwen3:1.7b", #Only model i could run locally. 
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
agent = Agent(
    ollama_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search DuckDuckGo for the given query and return the results.",
)
result = agent.run_sync(
    "Can you list the top five highest-grossing animated films of 2025?"
)
print(result.output)
print(result.usage())
