
from typing import List
from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    Load the embedding model only once.
    Reuse the same model throughout the application.
    """

    print("Loading Sentence Transformer model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Embedding model loaded successfully!")

    return model


class EmbeddingService:

    def __init__(self):
        self.model = get_embedding_model()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple repository chunks into embedding vectors.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Convert a user query into an embedding vector.
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return embedding.tolist()
