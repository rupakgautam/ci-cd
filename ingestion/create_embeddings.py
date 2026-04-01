import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documents")


def store_chunks(chunks, file_id=""):

    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        page = chunk["page"]

        embedding = model.encode(text).tolist()

        collection.add(
            ids=[f"{file_id}_{i}"],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"source": file_id, "page": page}],
        )
