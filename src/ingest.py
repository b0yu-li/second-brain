import os
import chromadb
from chromadb.utils import embedding_functions


def run_ingestion():
    client = chromadb.PersistentClient(path="./db")
    # Use local embeddings for speed and cost-efficiency
    # TODO: maybe can try sentence-transformers/all-MiniLM-L12-v2
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        "knowledge_base", embedding_function=emb_fn
    )

    # 1. Check if directory exists
    data_path = "./data"
    if not os.path.exists(data_path):
        print(f"❌ Error: Directory '{data_path}' not found!")
        return

    files = os.listdir(data_path)
    print(f"📂 Found {len(files)} files in {data_path}...")

    for filename in files:
        # 2. Case-insensitive extension check
        if filename.lower().endswith((".txt", ".md")):
            print(f"📖 Reading {filename}...")
            with open(os.path.join(data_path, filename), "r") as f:
                content = f.read()

            # 3. Improved Chunking Logic
            # Your current code filters out chunks < 20 characters.
            # If your file is very short, it might get ignored.
            chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 5]

            if not chunks:
                print(
                    f"⚠️ Warning: No valid chunks found in {filename}. Check your formatting!"
                )
                continue

            print(f"🧱 Adding {len(chunks)} chunks to database...")
            collection.add(
                documents=chunks,
                ids=[f"{filename}_{i}" for i in range(len(chunks))],
                metadatas=[{"source": filename} for _ in chunks],
            )
    print("✅ Knowledge Base Updated.")


if __name__ == "__main__":
    run_ingestion()
