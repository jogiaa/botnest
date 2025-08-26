from pathlib import Path

from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.chroma import ChromaDb

from poc_agno.llm_model_config import llm_model
from poc_agno.utils.load_instructions import load_yaml_instructions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
print(PROJECT_ROOT)
vector_db_chroma = ChromaDb(
    collection="food_knowledge",
    path=f"{PROJECT_ROOT}/chroma",
    persistent_client=True,
    embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
)
# pip install aiofiles
# without aiofiles, first time agent didn;t responded the query.
# it takes some time to fill the database
knowledge_base = JSONKnowledgeBase(
    path=PROJECT_ROOT,
    formats=[".food"],
    vector_db=vector_db_chroma
)

# Load the knowledge base (do this only the first time or when updating)
knowledge_base.load(recreate=False)

food_agent = Agent(
    name="Food Agent",
    role="You contains all the knowledge about food.",
    model=llm_model,
    instructions=load_yaml_instructions("food_knowledge_agent_instructions.yaml"),
    knowledge=knowledge_base,
    search_knowledge=True,
    # reasoning=True,
    # response_model=DocumentedResult,
    # show_tool_calls=True,
    # markdown=True,
    # debug_mode=True,
    # retriever=chroma_retriever
)

if __name__ == "__main__":
    food_agent.print_response("How many carbs in cheddar cheese")