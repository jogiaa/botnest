from typing import List

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.scrapegraph import ScrapeGraphTools
from agno.tools.spider import SpiderTools
from pydantic import BaseModel, Field

from poc_agno.llm_model_config import llm_model
from poc_agno.utils.load_instructions import load_yaml_instructions


class RecipieLinks(BaseModel):
    url: str = Field(..., description="Link to the recipe")
    rank: int = Field(..., description="Rank of the link")


class DishRecipies(BaseModel):
    dish_name: str = Field(..., description="Name of the dish")
    dish_recipies: List[RecipieLinks] = Field(..., description="List of recipe links for the dish")


food_search_agent = Agent(
    agent_id="002_recipie_search",
    description="You are recipie search agent that helps user find recipes",
    role="Recipie search agent",
    respond_directly=True,
    add_transfer_instructions=True,
    instructions=load_yaml_instructions("instructions.yaml"),
    model=llm_model,
    tools=[
        DuckDuckGoTools(search=True, news=False),
    ],
    response_model=DishRecipies,
    show_tool_calls=True,
    debug_mode=True,
    markdown=True
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
    food_search_agent.print_response("How to make mutton haleem?")
