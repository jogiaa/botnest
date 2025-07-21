from agno.team import Team

from poc_agno.agents.code_documenter import code_doc_agent
from poc_agno.agents.web_search_ddg_agent import web_agent
from poc_agno.llm_model_config import llm_model

scribe_team = Team(
    name="Code Documenter Team",
    mode="coordinate",
    members=[web_agent, code_doc_agent],
    model=llm_model,
    description="Extract source code from the input file. Add comments. Saved the modified code in the output file.",
    success_criteria="Code is documented.",
    instructions=[
        "You are versatile coder who can document the code in any programming language.",
        "Step 1: Extract the text from the input file. The file agent reads the file."
        "Step 2: Add documentation to the source code. The code doc agent adds documentation to the codebase.",
        "Step 3: The output from code doc agent is saved by the file agent.",
        "Each agent should only perform their assigned step and pass the result to the next agent.",
        # "Never change the original file's contents.",
    ],
    show_tool_calls=True,
    markdown=True,
    reasoning=True,
)
