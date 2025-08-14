from pathlib import Path
from pprint import pprint

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

embedding_fn = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
chroma_client = client = chromadb.PersistentClient(
    path=PROJECT_ROOT / "chroma",
)

summary_collection = chroma_client.get_or_create_collection(
    name="project_summaries",
    embedding_function=embedding_fn
)

knowledge_collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=embedding_fn
)


def store_result(data_content, data_path, collection=None, metadata=None):
    # Use default collection if not provided
    if collection is None:
        # Assuming knowledge_collection is defined elsewhere and accessible
        collection = summary_collection

    # Use default metadata if not provided
    if metadata is None:
        metadata = [{
            "file_path": data_path,
            "doc_type": "summary",
        }]

    if data_content and data_content.lower() != "skip":
        collection.add(
            documents=[data_content],
            metadatas=metadata,
            ids=[data_path]
        )
        print(f"✅ Saved summary for {data_path}")
    else:
        print(f"⚠️ Skipped {data_path} (empty or irrelevant)")


def get_all_summaries() -> str:
    all_docs = summary_collection.get(where={"doc_type": "summary"})
    return "\n\n".join(all_docs["documents"])


def get_all_code() -> str:
    all_docs = knowledge_collection.get(where={"doc_type": "code"})
    return "\n\n".join(all_docs["documents"])


def get_project_context(file_path: str, top_k: int = 5) -> str:
    results = summary_collection.query(
        query_texts=[file_path],
        n_results=top_k,
        where={"doc_type": "summary"},
    )
    return "\n".join(results["documents"][0]) if results["documents"] else ""


funny_collection = chroma_client.get_or_create_collection(
    name="funny_facts2",
    embedding_function=embedding_fn
)


def addData():
    funny_collection.add(documents=["Color of sky is green."], ids=["1"])


if __name__ == "__main__":
    # pprint(get_all_summaries())
    # print("---------")
    # addData()
    # ans = funny_collection.query(query_texts=["color of sky"])
    # pprint(ans)
    d = funny_collection.get()
    pprint(d)
    # pprint(get_all_code())
