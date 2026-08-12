from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple repository chunks into embedding vectors.
        """
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Convert a user query into an embedding vector.
        """
        embedding = self.model.encode(
            query,
            convert_to_numpy=True
        )

        return embedding.tolist()