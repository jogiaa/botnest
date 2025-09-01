import asyncio
from pathlib import Path
from pprint import pprint

import yaml
from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from humanfriendly.text import dedent
from pydantic import BaseModel

from poc_agno.llm_model_config import llm_model
from poc_agno.memory.chroma_code_context import funny_collection
from poc_agno.utils.load_instructions import load_yaml_instructions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

# TextKnowledgebase reads text files from a given path and saves them in chromadb
# so it needs a path to text files in order to work
# knowledge = TextKnowledgeBase(
#     path=PROJECT_ROOT,
#     vector_db=ChromaDb(
#         collection="knowledge_base",
#         path=f"{PROJECT_ROOT}/chroma",
#         persistent_client=True,
#         embedder=GeminiEmbedder()
#     )
# )

vector_db_chroma = ChromaDb(
    collection="code_base",
    path=f"{PROJECT_ROOT}/chroma",
    persistent_client=True,
    embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
)
# pip install aiofiles
# without aiofiles, first time agent didn;t responded the query.
# it takes some time to fill the database
knowledge_base = TextKnowledgeBase(
    path=PROJECT_ROOT,
    formats=[".pop"],
    vector_db=vector_db_chroma
)


# knowledge.load()


class DocumentedResult(BaseModel):
    original_code: str
    modified_code: str


def read_instructions() -> str:
    instructions = load_yaml_instructions(f"{Path(__file__).resolve().parent}/instructions.yaml")
    print(instructions)
    return instructions


def chroma_retriever(agent, query, num_documents=None, **kwargs):
    """
        Use the ChromaDb client directly to search your collection
    """
    # Return a list of dicts with 'content' keys
    results = funny_collection.query(query, n_results=num_documents or 5)
    print("***************")
    pprint(funny_collection.get())
    ddd = [{"content": r["text"]} for r in results]
    print("***************")
    pprint(ddd)
    print("***********")
    return ddd


delusional_agent = Agent(
    # name="Knowledge Agent",
    # role="You are a knowledge based agent. Show all of your knowledge",
    model=llm_model,
    instructions=read_instructions(),
    knowledge=knowledge_base,
    search_knowledge=True,
    # reasoning=True,
    # response_model=DocumentedResult,
    # show_tool_calls=True,
    # markdown=True,
    # debug_mode=True,
    # retriever=chroma_retriever
)


async def main():
    # Load the knowledge base (do this only the first time or when updating)
    await knowledge_base.aload(recreate=False)

    # pprint(vector_db_chroma.search(query="color of sky"))

    # Ask the agent a question
    await delusional_agent.aprint_response("Do men like color of sky?", markdown=True)


if __name__ == "__main__":
    asyncio.run(main())