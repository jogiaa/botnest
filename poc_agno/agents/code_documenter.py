from textwrap import dedent

from pydantic import BaseModel

from poc_agno.llm_model_config import llm_model, code_model
from agno.agent import Agent


class DocumentedResult(BaseModel):
    original_code: str
    modified_code: str


# Single-agent system that adds doc comments to code snippets
code_doc_agent = Agent(
    name="Code Documentation Agent",
    role="Add documentation comments to functions, methods, or classes",
    model=code_model,
    instructions=dedent("""
        You are a strict code documentation agent.

        Your job is to:
        - Detect the programming language (Python or Kotlin or java)
        - Add documentation comments to EVERY class, function, and method
        - DO NOT skip any item, even if it looks obvious or self-documenting
        - Use:
            - **Sphinx-style docstrings** for Python (triple-quoted before defs/classes)
            - **KDoc** for Kotlin
            - **Jdoc** for Java
        - DO NOT alter logic, variable names, spacing, or formatting
        - DO NOT comment import statements, assignments, or general logic blocks

        Return:
        - The FULL original code with documentation added in-place
        - No surrounding markdown, no explanation — just the modified code
    """),
    response_model=DocumentedResult,
    show_tool_calls=False,
    markdown=True,
)

if __name__ == "__main__":
    from pprint import pprint

    raw_code = dedent("""
        package org.koin.example

        class ElectricHeater : Heater {
        
            private var heating: Boolean = false
        
            override fun on() {
                println("~ ~ ~ heating ~ ~ ~")
                heating = true
            }
        
            override fun off() {
                heating = false
            }
        
            override fun isHot(): Boolean = heating
        }
     
     """)
    response = code_doc_agent.run(f"Add comments to the following code:\n\n{raw_code}")
    pprint(response.content.modified_code)
