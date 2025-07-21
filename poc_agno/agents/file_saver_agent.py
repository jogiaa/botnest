import logging
from pathlib import Path

from agno.agent import Agent
from agno.tools.file import FileTools
from agno.utils.log import LOGGER_NAME
from pydantic import BaseModel

from poc_agno.llm_model_config import llm_model

logging.getLogger(LOGGER_NAME).setLevel(logging.DEBUG)


class SearchResult(BaseModel):
    file_name: str
    content: str


path = Path("/var/tmp/carburetor/")
#
file_agent = Agent(
    name="File Handling Agent",
    role="To Read , write and list the files",
    instructions=[
        "Use this FileTools to read and write files locally.",
    ],
    model=llm_model,
    tools=[FileTools(path)],
    show_tool_calls=True,
    markdown=True,
)
#
# if __name__ == "__main__":
#     file_agent.print_response("read and print the names of files with extension py and save it to pp.txt", stream=True)


print(f"Found path {path}")
#
# for txt_file in path.glob('*.py'):
#     print(f"Found python file {txt_file}")

# file_agent = Agent(
#     # model=llm_model,
#     model=openai_model,
#     tools=[
#         FileTools(
#             save_files=True,
#             read_files=True,
#             list_files=True
#         )
#     ],
#     show_tool_calls=True
# )

# fa = Agent(
#     model=llm_model,
#     tools=[DuckDuckGoTools(search=True, fixed_max_results=10), FileTools(base_dir=path, save_files=True)],
#     instructions=[
#         "Follow the sequence as instructed",
#         "1 Search the web for answers.",
#         "2 Present findings in a structured, easy-to-follow format.",
#         "3 Use relevant name from search to name the file. Save file with extension txt",
#         f"4 If the user wants to save the response, use FileTools to save the response in the {path} configured in FileTools.",
#         "5 print the exact path of saved file"
#     ],
#     markdown=True,
#     stream=True,
#     show_tool_calls=True,
#     reasoning=True,
#     # response_model=SearchResult,
#     # debug_mode=True,
#
# )
# asyncio.run(
#     fa.aprint_response("Whats happening in France? Save results to a file.", )
# )

# FileTools(base_dir=path).save_file(file_name="jinjin.txt" ,contents= "something")


# def main():
#     file_agent.print_response(
#         "Use the file tool to list all .py files in  ~/PycharmProjects/carburetor",
#         markdown=True,
#         # stream=True
#     )
#
#
# if __name__ == '__main__':
#     main()
# asyncio.run(main())
#
# agent.print_response(
#     "list python files from /var/tmp/carburetor",
#     markdown=True,
#     stream=True
# )
# #
# print("Agent tools:", agent.tools)
# print("Agent memory:", agent.memory)
# print("Agent LLM:", agent.model)
