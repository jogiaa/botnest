import os
from pprint import pprint

from agno.agent import Agent
from agno.tools import tool
from dotenv import load_dotenv

from poc_agno.llm_model_config import llm_model
from poc_agno.mrcarbs.worker.usda_fsdc_client import FoodCarbFinder
from poc_agno.utils.load_instructions import load_yaml_instructions


@tool(name="food carb search tool")
def get_food_carbs(food_name: str, exact: bool = False) -> dict:
    """
    Look up carbohydrate information for a given food.

    Args:
        food_name: Name of the food (e.g., 'apple', 'red delicious apple').
        exact: If True, requires an exact description match.

    Returns:
        A dict with:
            - description: matched food description
            - per_100g: carbs per 100 grams
            - per_serving: list of servings with carb values
    """

    load_dotenv()
    print("----------------------------")
    finder = FoodCarbFinder(api_key=os.getenv("USDA_API_KEY"))
    desc, carbs = finder.get_carbs(food_name, exact)
    if not desc or not carbs:
        return {"error": f"No food found for '{food_name}'"}
    return {"description": desc, **carbs}


# if __name__ == "__main__":
#     agent = Agent(
#         model=llm_model,
#         tools=[get_food_carbs],
#         show_tool_calls=True,
#         instructions=load_yaml_instructions("../agent/food_search/instructions.yaml")
#     )
#
#     pprint(agent.run("How many carbs are in a medium red delicious apple?"))
