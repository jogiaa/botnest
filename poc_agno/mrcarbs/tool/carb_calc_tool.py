from agno.tools import tool
from pydantic import BaseModel, Field

from poc_agno.utils import get_builtin_logger


class CarbCalcInput(BaseModel):
    per_100g: float = Field(..., description="Carbs per 100 grams of the food")
    grams: float = Field(..., description="Total grams of the portion")


@tool(name="carb_calculator_tool", strict=True, show_result=True)
def carb_calculator_tool(per_100g: float, grams: float) -> float:
    """
    Deterministically calculate carbs from per_100g value and weight in grams.
    """
    logger = get_builtin_logger()
    result =  round(per_100g * (grams / 100), 2)
    logger.debug(f"{grams}[Portion] --- {per_100g}[per 100g]  = {result} [result]")
    return result
