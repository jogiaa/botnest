import os
from pathlib import Path
from typing import Callable, Dict, Any

from agno.tools import tool, FunctionCall
from dotenv import load_dotenv

from poc_agno.mrcarbs.worker.usda_fsdc_client import FoodCarbFinder

cache_path = Path(__file__).parent / ".cache_food_carb_search"

def sanitize_params_for_tool(fc: FunctionCall):
    """
    Commander Safeguard:Sanitizing the params for the tool before the call is made to the tool.
    Even though there are strict instructions not to add extra params,
    sometimes LLM gets high and introduce unwanted stuff ...
    """
    print(f"Pre-hook: {fc.function.name}")
    print(f"Arguments: {fc.arguments} {type(fc.arguments)}")
    #
    fc.arguments = {'food_name': fc.arguments['food_name'].lower().strip()}
    print(f"Modified Arguments: {fc.arguments}")


def post_hook(fc: FunctionCall):
    """
    Not necessary for the overall working of the tool just for learning
    """
    print(f"Post-hook: {fc.function.name}")
    print(f"Arguments: {fc.arguments}")
    print(f"Result: {fc.result} {type(fc.result)}")
    # fc.result.update({'description': fc.result['description'].lower()})
    print(f"After modification Result: {fc.result}")


@tool(
    name="get_food_carbs_tool",
    show_result=True,
    cache_results=True,
    strict=True,
    cache_dir=cache_path.absolute().name,
    pre_hook=sanitize_params_for_tool,
    post_hook=post_hook,
    # this empty tool list is there to make sure that cache works.
    # If its None the code has a bug which doesn't use cache
    tool_hooks=[]
)
def get_food_carbs(food_name: str) -> dict:
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
    desc, carbs = finder.get_carbs(food_name, False)
    if not desc or not carbs:
        return {"error": f"No food found for '{food_name}'"}
    return {"description": desc, **carbs}
#
# if __name__ == "__main__":
#     PROJECT_ROOT = Path(__file__).resolve().parent.parent
#     print(PROJECT_ROOT)
#     agent = Agent(
#         model=llm_model,
#         tools=[get_food_carbs],
#         show_tool_calls=True,
#         instructions=load_yaml_instructions(f"{PROJECT_ROOT}/agent/food_search/instructions.yaml")
#     )
#
#     pprint(agent.run("How many carbs are in a medium red delicious apple?"))
