from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

from poc_agno.llm_model_config import llm_model

web_agent = Agent(
    name="Web Agent",
    role="Search the web for recipes and nutritional information",
    model=llm_model,
    tools=[DuckDuckGoTools(search=True, fixed_max_results=10)],
    instructions="Always include sources",
    show_tool_calls=False,
    markdown=False,
)
