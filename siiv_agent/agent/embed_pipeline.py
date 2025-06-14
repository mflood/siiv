from pathlib import Path
from argparse import ArgumentParser
from tqdm import tqdm
from typing import List
import requests
import chromadb
from chromadb.config import Settings

from code_chunker import extract_code_chunks, CodeChunk

LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/embeddings"  # Adjust port if needed
CHUNK_TEXT = "This is a chunk of text to embed using LM Studio."
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5e04_k_m" # Use model name you have loaded
EMBEDDING_MODEL2 = "text-embedding-nomic-embed-text-v1.5e0q.0"
CHROMA_COLLECTION_NAME="code_chunks"

def embed_text(text: str) -> list[float]:
    response = requests.post(
        LM_STUDIO_ENDPOINT,
        json={
            "model": EMBEDDING_MODEL,
            "input": [text],
            "encoding_format": "float"
        }
    )

    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def process_repo(
    repo_path: Path,
):
    chroma_client = chromadb.Client(Settings(persist_directory=str(chroma_path)))
    chroma_client = chromadb.PersistentClient(path=".chroma_storage")
    collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

    py_files = list(repo_path.rglob("*.py"))
    for file in tqdm(py_files, desc="🗃 Processing files"):
        for chunk in extract_code_chunks(file):
            try:
                embedding = embed_text(chunk.code)
                metadata = chunk.to_metadata_dict()
                #print(f"chunk: {chunk.code}")
                #print(f"chunk.code: {chunk.code}")
                #print(f"embedding: {embedding}")

                collection.add(
                    documents=[chunk.code],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    ids=[f"{chunk.file_path}:{chunk.start_line}-{chunk.end_line}"]
                )
            except Exception as e:
                print(f"⚠️ Failed to process chunk in {chunk.file_path}:{chunk.start_line}-{chunk.end_line}: {e}")
                print(chunk)
                raise

    print("✅ All chunks embedded and stored.")

if __name__ == "__main__":
    parser = ArgumentParser(description='Embed Python code chunks and store in ChromaDB')
    parser.add_argument("--repo", type=Path, required=True, help="Path to the root of the Python repository")
    args = parser.parse_args()

    process_repo(
        repo_path=args.repo,
    )
