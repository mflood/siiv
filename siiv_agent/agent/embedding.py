from argparse import ArgumentParser
from pathlib import Path
from typing import List

import chromadb
import requests
from chromadb.config import Settings
from tqdm import tqdm

LOGGER_NAME = __name__

LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/embeddings"

# ensure lm-studio is running the same embedding model used to load
# the vector store
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5@e9.0"
EMBEDDING_MODE = "lm-studio ignores this and just uses whatever is loaded"
CHROMA_COLLECTION_NAME = "code_chunks"

# get lf embedding from LM Studio
def get_lm_studio_embedding(text: str) -> List[float]:
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Calling lm-studio API to embed text: '%s'", text)

    payload = {"model": EMBEDDING_MODEL, "input": [text], "encoding_format": "float"}
    try:
        response = requests.post(LM_STUDIO_ENDPOINT, json=payload)
        response.raise_for_status()
        embedding = response.json()['data'][0]['embedding']
        logger.info("First 5 values: %s", embedding[:5])
        return response.json()['data'][0]['embedding']
    except requests.RequestException as e:
        print(f"Error fetching embedding: {e}")
        return None

# Main execution
if __name__ == "__main__":
    import sys

    import my_logging

    text = "Embed this text"

    if len(sys.argv) > 1:
        text = sys.argv[1]
    vector = get_lm_studio_embedding(text)
