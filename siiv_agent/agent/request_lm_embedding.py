import requests
from chromadb.config import Settings

# Configuration
LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/embeddings"  # Adjust port if needed
CHUNK_TEXT = "This is a sample chunk of text to embed using LM Studio."
EMBEDDING_MODEL = (
    "text-embedding-nomic-embed-text-v1.5qeq4_k_m"  # Use model name you have loaded
)
CHROMA_COLLECTION_NAME = "my_collection"


# Step 1. Get embedding from LM Studio
def get_embedding(text: str, model: str):
    payload = {"model": model, "input": text, "encoding_format": "float"}
    try:
        response = requests.post(LM_STUDIO_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except requests.RequestException as e:
        print(f"Error fetching embedding: {e}")
        return None


# Step 2: Add to Chroma DB
def store_in_chroma(text: str, embedding: list, collection_name: str = "my_collection"):
    # Initialize Chroma client
    client = chromadb.PersistentClient(path="./chroma_storage")

    # client = chromadb.Client(Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name=collection_name)

    # Add document with embedding
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=["doc-1"],  # Make sure this ID is unique in your context
    )
    print("Stored embedding in Chroma DB.")


# Main execution
if __name__ == "__main__":
    vector = get_embedding(CHUNK_TEXT, EMBEDDING_MODEL)
    if vector:
        store_in_chroma(CHUNK_TEXT, vector)
