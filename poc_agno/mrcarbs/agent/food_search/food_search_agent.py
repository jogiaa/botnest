import asyncio
from pprint import pprint

from agno.agent import Agent

from poc_agno.llm_model_config import llm_model
from poc_agno.mrcarbs.tool.food_search_tool import get_food_carbs
from poc_agno.utils.load_instructions import load_yaml_instructions

food_search_agent = Agent(
    instructions=load_yaml_instructions("instructions.yaml"),
    model=llm_model,
    tools=[get_food_carbs],
    show_tool_calls=True,
    debug_mode=True,
)


async def main():
    result = await food_search_agent.arun("How many carbs are in a 1lb of green beans?")
    pprint(result)


if __name__ == "__main__":
    asyncio.run(main())


