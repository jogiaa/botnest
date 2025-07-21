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


def store_result(data_content, data_path):
    if data_content and data_content.lower() != "skip":
        summary_collection.add(
            documents=[data_content],
            metadatas=[{
                "file_path": data_path,
                "doc_type": "summary",
            }],
            ids=[data_path]
        )

        print(f"✅ Saved summary for {data_path}")
    else:
        print(f"⚠️ Skipped {data_path} (empty or irrelevant)")


def get_all_summaries() -> str:
    all_docs = summary_collection.get(where={"doc_type": "summary"})
    return "\n\n".join(all_docs["documents"])


def get_project_context(file_path: str, top_k: int = 5) -> str:
    results = summary_collection.query(
        query_texts=[file_path],
        n_results=top_k,
        where={"doc_type": "summary"},
    )
    return "\n".join(results["documents"][0]) if results["documents"] else ""



if __name__ == "__main__":
    pprint(get_all_summaries())