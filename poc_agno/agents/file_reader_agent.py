from agno.agent import Agent
from agno.tools.file import FileTools
from pydantic import BaseModel, Field
from typing import Optional

from poc_agno.llm_model_config import llm_model, code_model


class FileReadResult(BaseModel):
    """Response model for file reading agent"""
    file_path: str = Field(description="Path of the file that was read")
    file_content: str = Field(description="Content read from the file")
    # file_size: int = Field(description="Size of the file in bytes")
    # success: bool = Field(description="Whether the file was successfully read")
    # error_message: Optional[str] = Field(description="Error message if reading failed", default=None)


file_reader: Agent = Agent(
    name="File Reader",
    model=llm_model,
    tools=[FileTools(read_files=True, save_files=False)],
    description="Reads file content from a specified path",
    instructions=[
        "You are a file reading specialist.",
        "Use the FileTools read_file function to read the content of a file from the specified path.",
        "The read_file function takes a file_name parameter.",
        "Extract the actual file content from the tool response, not just the tool name.",
        "Return the file content along with metadata like file size.",
        "Handle errors gracefully and provide clear error messages.",
        "Ensure you return a structured response with all required fields."
    ],
    response_model=FileReadResult,
    show_tool_calls=True,
    # reasoning=True,
    markdown=True,
)

if __name__ == "__main__":
    ### DAMN THING DOESNT WORK STILL
    source_file_path = "./poc_agno/api/main.py"
    result = file_reader.run(f"Read the file content from path: {source_file_path}")
    print(result.content)
