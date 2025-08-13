import asyncio
from pathlib import Path

from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.reranker.cohere import CohereReranker
from agno.vectordb.chroma import ChromaDb
from humanfriendly.text import dedent

from poc_agno.llm_model_config import llm_model
from poc_agno.workflows.v2_workflow.load_instructions import load_agent_instructions

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# source = "SampleCode/sample-lib/src/main/java/org/jay/sample"
# source_path = str(Path(PROJECT_ROOT / source).absolute())
#
# print(source_path)

vector_db_chroma = ChromaDb(
    collection="code_base",
    path=f"{PROJECT_ROOT}/chroma",
    persistent_client=True,
    embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
    reranker=CohereReranker(model="rerank-v3.5")
)

knowledge_base = TextKnowledgeBase(
    path=PROJECT_ROOT,
    formats=[".kt"],
    vector_db=vector_db_chroma
)

knowledgeable_code_documentation_agent = Agent(
    model=llm_model,
    instructions=dedent(load_agent_instructions("instructions2.yaml")),
    knowledge=knowledge_base,
    search_knowledge=True,
    reasoning=True,
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
)


async def main():
    source = "SampleCode/sample-lib/src/main/java/org/jay/sample"
    source_path = str(Path(PROJECT_ROOT / source).absolute())
    print(source_path)
    await knowledge_base.aload(source_path)
    # async for doc in knowledge_base.async_document_lists:
    #     print("*"*50)
    #     print(doc)
    #     print("*"*50)

    # d = await knowledge_base.vector_db.async_search("Logger")
    # print(d)

    await knowledgeable_code_documentation_agent.aprint_response("Document 'Logger' class.")

if __name__ == "__main__":
    asyncio.run(main())
