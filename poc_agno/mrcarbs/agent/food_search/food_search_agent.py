import asyncio
from pprint import pprint

from agno.agent import Agent

from poc_agno.llm_model_config import llm_model
from poc_agno.mrcarbs.tool.carb_calc_tool import carb_calculator_tool
from poc_agno.mrcarbs.tool.food_search_tool import get_food_carbs
from poc_agno.utils.load_instructions import load_yaml_instructions

food_search_agent = Agent(
    agent_id="001_food_search",
    instructions=load_yaml_instructions("instructions.yaml"),
    model=llm_model,
    tools=[get_food_carbs , carb_calculator_tool],
    show_tool_calls=True,
    # debug_mode=True,
    markdown= True
)


# async def main():
#     result = await food_search_agent.arun("How many carbs are in a 1lb of green beans?")
#     pprint(result)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


if __name__ == "__main__":
    pprint(food_search_agent.run("How many carbs are in a large size banana?"))
