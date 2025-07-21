import chromadb

client = chromadb.Client()
# Create a collection
collection = client.get_or_create_collection("my_collection")
# Insert some data
collection.add(documents=["Cairo is the capital of Egypt."], ids=["1"])

print(collection.query(query_texts=["capital of Egypt"], n_results=1))