from pprint import pprint

from agno.team import Team
from pydantic import BaseModel

from poc_agno.agents.simplest_math_agent import math_agent
from poc_agno.agents.web_search_ddg_agent import web_agent
from poc_agno.llm_model_config import llm_model
from poc_agno.utils.load_instructions import load_yaml_instructions



class CarbInfo(BaseModel):
    ingredients: str
    ingredient_carbs: str

class DishCarbInfo(BaseModel):
    dish: str
    ingredients: list[CarbInfo]
    carbs: float


agent_team = Team(
    mode="coordinate",
    members=[web_agent, math_agent],
    model=llm_model,
    description="Search recipes and estimate carbs content per serving.",
    success_criteria="Find accurate or estimated carbs count using web search and calculations.",
    instructions=load_yaml_instructions("instructions.yaml"),
    response_model=DishCarbInfo,
    show_tool_calls=True,
    markdown=True,
    reasoning=True,
    debug_mode=True,
)

if __name__ == "__main__":
    agent_team.print_response("Find carbs of one bowl of Mutton Haleem?", stream=True)
