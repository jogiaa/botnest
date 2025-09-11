from agno.debug import enable_debug_mode
from agno.team import Team
from pydantic import BaseModel, Field

from poc_agno.llm_model_config import llm_model, code_model
from poc_agno.mrcarbs.agent.food_search.food_search_agent import food_search_agent
from poc_agno.mrcarbs.agent.recipie_search.recipie_search_agent import recipe_aggregator_agent
from poc_agno.utils.load_instructions import load_yaml_instructions

enable_debug_mode()

class DishCarbInfo(BaseModel):
    dish: str = Field(..., description="Dish name")
    servings: int = Field(..., description="Servings")
    carbs_per_serving_g: float = Field(..., description="Carbs per serving in grams")


agent_team = Team(
    name="003_CarbPerServingCalculator",
    role="""
    The CarbPerServingCalculator agent computes the carbohydrate content per serving of a 
    dish by pulling recipe data from 002_RecipeAggregator, looking up ingredient 
    carb values with 001_food_search, and returning the result in a concise JSON format.
    """,
    description="""
    Orchestrates carb calculations for a dish by consuming structured recipe data from 
    002_RecipeAggregator, querying 001_food_search for ingredient carbs, and returning 
    the carb amount per serving in a clean JSON format.""",
    mode="coordinate",
    members=[recipe_aggregator_agent, food_search_agent],
    model=llm_model,
    success_criteria="Accurately determine or estimate the carbohydrate content of a dish by retrieving data through given team members and web",
    instructions=load_yaml_instructions("instructions.yaml"),
    # response_model=DishCarbInfo,
    show_tool_calls=True,
    markdown=False,
    # reasoning=True,
    debug_mode=True,
    add_datetime_to_instructions=True,
    add_member_tools_to_system_message=True,
    parser_model=code_model,
    use_json_mode=True,
    debug_level=2,
    show_members_responses=True
)

if __name__ == "__main__":
    agent_team.print_response("Find carbs of one bowl of calm chowder?")
