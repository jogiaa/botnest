from agno.tools.calculator import CalculatorTools
from agno.agent import Agent

from poc_agno.llm_model_config import llm_model

math_agent = Agent(
    name="Math Agent",
    role="Perform mathematical calculations",
    model=llm_model,
    tools=[CalculatorTools()],
    instructions="Show all steps in calculations",
    # instructions="Use markdown for mathematical expressions and all the steps in calculations",
    show_tool_calls=True,
    markdown=True,
)


if __name__ == "__main__":
    math_agent.run("how much would it cose if 34% is off from original price of 3456")
