import chromadb
from chromadb.config import Settings

# Initialize Chroma client
client = chromadb.PersistentClient(path="./chroma_storage")
#client = chromadb.Client(Settings(
    #    anonymized_telemetry=False),
#    chroma_db_impl="duckdb+parquet",
#    persist_directory="./chroma_storage",
#    )
collection = client.get_or_create_collection(name="code_chunks")

# --- CRUD Functions ---

def create_document(doc_id: str, text: str, embedding: list = None):
    """Create or add a document with optional embedding."""
    try:
        collection.add(documents=[text], ids=[doc_id], embeddings=[embedding] if embedding else None)
        print(f"✅ Created document with ID: {doc_id}")
    except Exception as e:
        print(f"❌ Failed to create document: {e}")

def read_document(doc_id: str):
    """Read/retrieve a document by ID."""
    try:
        result = collection.get(ids=[doc_id], include=["documents", "embeddings", "metadatas"])
        print(f"📄 Document found: {result}")
        return result
    except Exception as e:
        print(f"❌ Failed to read document: {e}")

def update_document(doc_id: str, new_text: str, new_embedding: list = None):
    """Update a document by deleting it and re-adding it."""
    try:
        collection.delete(ids=[doc_id])
        collection.add(documents=[new_text], ids=[doc_id], embeddings=[new_embedding] if new_embedding else None)
        print(f"🔄 Updated document with ID: {doc_id}")
    except Exception as e:
        print(f"❌ Failed to update document: {e}")

def delete_document(doc_id: str):
    """Delete a document by ID."""
    try:
        collection.delete(ids=[doc_id])
        print(f"🗑️ Deleted document with ID: {doc_id}")
    except Exception as e:
        print(f"❌ Failed to delete document: {e}")

def list_all_ids():
    """List all object/document IDs in the collection."""
    try:
        # Set a high limit to retrieve all items; adjust as needed
        #results = collection.get(include=['ids'], limit=1000)
        results = collection.get(limit=1000)
        ids = results['ids']
        print(f"✅ All document IDs: {ids}")
        return ids
    except Exception as e:
        print(f"❌ Failed to list document IDs: {e}")
        return []

# === Example usage ===
if __name__ == "__main__":
    # List all document IDs
    list_all_ids()
    # List again
    # list_all_ids()

    doc_id = "doc-1"
    original_text = "This is the original document."
    updated_text = "This is the updated version of the document."

    # Create
    create_document(doc_id, original_text)

    # Read
    read_document(doc_id)

    # Update
    update_document(doc_id, updated_text)

    # Read again
    read_document(doc_id)

    # List all IDs
    # list_all_ids()

    # Delete
    delete_document(doc_id)

    # Confirm deletion
    read_document(doc_id)

    # List again
    list_all_ids()
