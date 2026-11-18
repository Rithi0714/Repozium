
from typing import List, Dict, Any

from src.vectorstore import VectorStore


class Retriever:

    def __init__(
        self,
        top_k: int = 10,
        collection_name: str = "repository_code"
    ):
        self.top_k = top_k

        # Search more candidates than we ultimately need.
        self.candidate_k = max(top_k * 2, 18)

        self.vector_store = VectorStore(
            collection_name=collection_name
        )

    def retrieve(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            return []

        results = self.vector_store.search(
            query=query.strip(),
            top_k=self.candidate_k
        )

        documents = (results.get("documents") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]

        candidates = []
        seen_chunks = set()

        for index, document in enumerate(documents):

            if not document or not document.strip():
                continue

            normalized_content = document.strip()

            if normalized_content in seen_chunks:
                continue

            seen_chunks.add(normalized_content)

            metadata = (
                metadatas[index]
                if index < len(metadatas) and metadatas[index]
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            candidates.append({
                "content": document,
                "metadata": metadata,
                "distance": distance,
                "file_path": metadata.get("file_path", "Unknown file"),
                "language": metadata.get("language", "Unknown"),
                "chunk_type": metadata.get("chunk_type", "Unknown"),
                "class_name": metadata.get("class_name", ""),
                "function_name": metadata.get("function_name", "")
            })

        # First pass: select the best matching chunk from
        # each different file.
        selected = []
        selected_ids = set()
        seen_files = set()

        for chunk in candidates:

            file_path = chunk["file_path"]

            if file_path not in seen_files:
                selected.append(chunk)
                selected_ids.add(id(chunk))
                seen_files.add(file_path)

            if len(selected) >= self.top_k:
                return selected

        # Second pass: fill remaining slots with other
        # relevant chunks, including additional chunks
        # from files already selected.
        for chunk in candidates:

            if id(chunk) in selected_ids:
                continue

            selected.append(chunk)
            selected_ids.add(id(chunk))

            if len(selected) >= self.top_k:
                break

        return selected
