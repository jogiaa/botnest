from agno.team import Team
from pydantic import BaseModel

from poc_agno.agents.simplest_math_agent import math_agent
from poc_agno.agents.web_search_ddg_agent import web_agent
from poc_agno.llm_model_config import llm_model


class CarbData(BaseModel):
    dish: str
    carbs: float


agent_team = Team(
    mode="coordinate",
    members=[web_agent, math_agent],
    model=llm_model,
    description="I search for recipes and estimate their carbs content.",
    success_criteria="Find the carbs count using web search and calculations.",
    instructions=[
        "Search web for 5 recipes of the dish",
        "Extract common ingredients from the recipes",
        "List their carbs count",
        "Determine how recipe is prepared , cooking time, and serving size",
        "Based on the preparation instruction and serving size, estimate the total carbs",
        "before sending carbs to calculator make sure they are only numbers",
        "Use markdown for mathematical expressions and show all steps in calculations",
        "Provide a clear and concise answer with sources",
        "If the recipe is not found, provide a general estimate based on common ingredients"
    ],
    response_model=CarbData,
    show_tool_calls=True,
    markdown=True,
    reasoning=True,
    # debug_mode=True,
)

if __name__ == "__main__":
    agent_team.print_response("Find carbs of one bowl of Mutton Haleem?", stream=True)
