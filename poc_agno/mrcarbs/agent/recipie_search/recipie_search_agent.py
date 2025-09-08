from typing import List

from agno.agent import Agent
from agno.tools import FunctionCall
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field, confloat, PositiveInt

from poc_agno.llm_model_config import llm_model, code_model
from poc_agno.utils.load_instructions import load_yaml_instructions


class Ingredient(BaseModel):
    """Represents a single ingredient in a recipe."""

    name: str = Field(..., description="Ingredient name")
    quantity: confloat(ge=0) = Field(
        ...,
        description="Maximum quantity found across the fetched recipes",
    )
    unit: str = Field(..., description="Unit of measurement (e.g., grams, milliliters, cups)")


class RecipeResponse(BaseModel):
    """The JSON‑like response returned by the RecipeAggregator agent."""

    recipe_name: str = Field(..., description="Representative name of the dish.")
    links: List[str] = Field(
        ...,
        description="Exactly five URLs to reputable recipe sources",
    )
    ingredients: List[Ingredient] = Field(
        ...,
        description="Aggregated list of ingredients with maximum quantities",
    )
    summary: str = Field(
        ...,
        description="Condensed preparation summary (≤80 words)",
    )
    servings: PositiveInt = Field(
        ...,
        description="Number of people the recipe can feed",
    )


food_search_agent = Agent(
    agent_id="002_RecipeAggregator",
    description="You are recipie search agent that helps user find recipes and extract the ingredients and cooking summary",
    role="Recipe search agent",
    add_transfer_instructions=True,
    instructions=load_yaml_instructions("instructions.yaml"),
    model=llm_model,
    response_model=RecipeResponse,
    show_tool_calls=True,
    debug_mode=True,
    markdown=False,
    # expected_output= ,
    use_json_mode=True,
    parser_model=code_model,
    goal="The RecipeAggregator agent’s purpose is to fetch, consolidate, and present a reliable, concise overview of a requested dish by retrieving five reputable recipes, aggregating ingredient quantities (selecting the largest value when discrepancies arise), determining a representative dish name and serving size, and providing a succinct preparation summary, all while strictly adhering to the defined output schema and refraining from any extraneous responses."
)

if __name__ == "__main__":
    food_search_agent.print_response("recipie clam chowder?")
