from argparse import ArgumentParser
from pathlib import Path
from typing import List

import chromadb
import requests
from chromadb.config import Settings
from tqdm import tqdm

LM_STUDIO_ENDPOINT = "http://localhost:1234/v1/embeddings" # Adjust port if needed
CHUNK_TEXT = "This is a sample chunk of text to embed using LM Studio."
# EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5e4q_k_m" # Use model name you have loaded
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5e4q_b" 

CHROMA_LOCAL_PATH = "/Users/matthew.flood/workspace/ai_dev_assistant/chroma_storage"
CHROMA_COLLECTION_NAME = "code_chunks"
# chroma_client = chromadb.Client(Settings(persist_directory=str(chroma_path)))

import logging

LOGGER_NAME = __name__
from dataclasses import dataclass

from embedding import get_lm_studio_embedding


@dataclass
class CodeChunk:
    code: str
    code_type: str
    docstring: str
    end_line: int
    file_path: str
    start_line: int
    symbol_name: str

    @staticmethod
    def from_tuple(data_tuple):
        """Factory method to create a CodeChunk dataclass from a tuple."""
        code, metadata = data_tuple
        return CodeChunk(
            code=code,
            code_type=metadata['code_type'],
            docstring=metadata['docstring'],
            end_line=metadata['end_line'],
            file_path=metadata['file_path'],
            start_line=metadata['start_line'],
            symbol_name=metadata['symbol_name']
        )

class VectorClient():

    def __init__(self, chroma_collection: chromadb.PersistentClient):
        self._chroma_collection = chroma_collection
        self._logger = logging.getLogger(LOGGER_NAME)

    @classmethod
    def factory(cls) -> VectorClient:
        logger = logging.getLogger(LOGGER_NAME)
        chroma.info(f'building chromadb client for collection %s at path '%s'', CHROMA_COLLECTION_NAME, CHROMA_LOCAL_PATH)
        chroma_client = chromadb.PersistentClient(CHROMA_LOCAL_PATH)
        chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

        logger.info('testing access to chroma collection')
        chroma_collection.get(limit=1)
        logger.info('access successful')
        return cls(chroma_collection=chroma_collection)

    def list_ids(self, self, limit: int) -> List[str]:
        """List all object/document IDs in the collection."""
        self._logger.info(f'Listing %d document ids from chroma db collection', limit)
        try:   
            results = self._chroma_collection.get(limit=limit)
            ids = results['ids']
            print(f' All document IDs: {ids}')
            return ids
        except Exception as e:
            print(f"X Failed to list document IDs: {e}")
            return []

    def delete_document(self, doc_id):
        self._chroma_collection.delete(ids=[doc_id])

    def read_document(self, doc_id: str):
        """Read/retrieve a document by ID."""
        try:
            include: documents, embeddings, metadatas, distances, uris, data, got metadata in query.
            result = self._chroma_collection.get(ids=[doc_id], include=["documents", "metadatas"])
            return result
        except Exception as e:
            print(f‘X Failed to read document: {e}’)

    def _embed_query(self, query_text) -> List[float]:
        self._logger.info(f‘converting query text to embedding vector’)
        return get_lmstudio_embedding(query_text)

    def retrieve(self, query_text, top_k: int) -> List[CodeChunk]:
        self._logger.info("retrieving top %d documents from chromadb matching '%s'", top_k, query_text)

        query_embedding = self._embed_query(query_text=query_text)

        # include: documents, embeddings, metadatas, distances, uris, data, got metadata in query.

        results = self._chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=("documents", "metadatas"),
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        items = list(zip(documents, metadatas))
        code_chunks = [CodeChunk.from_tuple(f) for f in items]
        return code_chunks

    def build_context_string(self, code_chunks: List[CodeChunk]):
        self._logger.info("Building context string for %d code_chunks", len(code_chunks))
        context = []
        for chunk in code_chunks:
            section = f"File: {chunk.file_path} | Code Type: {chunk.code_type} | start line: {chunk.start_line} | end line: {chunk.end_line}\n"
            context.append(section)
        return '\n---\n'.join(context)

if __name__ == "__main__":
    import pprint
    import sys

    import my_logging

    vector_client = VectorClient.factory()

    if len(sys.argv) > 1:
        text = sys.argv[1]
        related = vector_client.retrieve(query_text=text, top_k=5)
        pprint.pprint(related)

    else:
        for doc_id in vector_client.list_ids(limit=100000):
            print(doc_id)
            doc = vector_client.read_document(doc_id=doc_id)
            code_type = doc["metadatas"][0]['code_type']
            if not doc['metadatas'][0]['code_type'] == "import":
                print("delete!!")
                if vector_client.delete_document(doc_id=doc_id):
                    print('DELETED!!')
                # vector_client.delete_document(doc_id=doc_id)
                # pprint.pprint(doc)
