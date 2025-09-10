from agno.agent import Agent

from poc_agno.llm_model_config import llm_model
from poc_agno.mrcarbs.tool.carb_calc_tool import carb_calculator_tool
from poc_agno.mrcarbs.tool.food_search_tool import get_food_carbs
from poc_agno.utils.load_instructions import load_yaml_instructions

food_search_agent = Agent(
    agent_id="001_food_search",
    name="food_search",
    role="""
    Dedicated carbohydrate‑nutrition assistant that answers user queries about the carbohydrate content 
    of foods. It operates strictly through the registered tools get_food_carbs_tool and carb_calculator_tool, 
    applying the prescribed rules for query normalisation, unit conversion, serving‑size estimation, 
    and calculation.
    """,
    description=""""
    It normalises the user’s query to a plain food name, fetches the per‑100g 
    carbohydrate value via get_food_carbs_tool, converts or estimates the requested weight 
    in grams, and then calls carb_calculator_tool with only {per_100g, grams} to produce an 
    accurate carbohydrate total, delivering the result without any additional commentary.
    """,
    instructions=load_yaml_instructions("instructions.yaml"),
    model=llm_model,
    tools=[get_food_carbs, carb_calculator_tool],
    show_tool_calls=True,
    debug_mode=True,
    markdown=False,
    goal="""
    To return a precise carbohydrate value (in grams) for any requested food item, using only the two 
    approved tools and adhering to the workflow defined below. No internal calculations, 
    hallucinations, or extraneous responses are permitted.
    """

)

# async def main():
#     result = await food_search_agent.arun("How many carbs are in a 1lb of green beans?")
#     pprint(result)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


if __name__ == "__main__":
    # pprint(food_search_agent.run("How many carbs are in a large size banana?"))
    food_search_agent.print_response("How many carbs are in a banana?")
