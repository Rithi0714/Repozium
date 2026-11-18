
from pathlib import Path
from typing import List, Dict, Any
import hashlib

import chromadb

from src.embeddings import EmbeddingService


class VectorStore:

    def __init__(
        self,
        persist_directory: str = "data/chroma",
        collection_name: str = "repository_code"
    ):
        self.persist_directory = Path(persist_directory)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        # Reuses the globally cached embedding model.
        self.embedding_service = EmbeddingService()

    def _create_chunk_id(self, chunk: Dict[str, Any]) -> str:
        """
        Create a stable unique ID for a repository chunk.
        """

        unique_text = (
            f"{chunk.get('file_path', '')}:"
            f"{chunk.get('class_name', '')}:"
            f"{chunk.get('function_name', '')}:"
            f"{chunk.get('start_line', '')}:"
            f"{chunk.get('end_line', '')}:"
            f"{chunk.get('chunk_id', '')}"
        )

        return hashlib.sha1(
            unique_text.encode("utf-8")
        ).hexdigest()

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Generate embeddings and store repository chunks in ChromaDB.
        """

        if not chunks:
            return

        documents = [
            chunk.get("content", "")
            for chunk in chunks
        ]

        embeddings = self.embedding_service.embed_documents(
            documents
        )

        ids = [
            self._create_chunk_id(chunk)
            for chunk in chunks
        ]

        metadatas = []

        for chunk in chunks:
            metadata = {
                "file_path": chunk.get("file_path") or "",
                "language": chunk.get("language") or "",
                "chunk_type": chunk.get("chunk_type") or "",
                "class_name": chunk.get("class_name") or "",
                "function_name": chunk.get("function_name") or "",
                "start_line": chunk.get("start_line") or 0,
                "end_line": chunk.get("end_line") or 0,
            }

            metadatas.append(metadata)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Search the repository for chunks relevant to a user query.
        """

        query_embedding = self.embedding_service.embed_query(
            query
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )

        return results

    def count(self) -> int:
        """
        Return the number of stored repository chunks.
        """

        return self.collection.count()
