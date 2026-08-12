from src.embeddings import EmbeddingService


def test_embedding():

    embedding_service = EmbeddingService()

    text = "This function handles user authentication."

    vector = embedding_service.embed_query(text)

    print("Embedding generated successfully!")
    print("Vector length:", len(vector))
    print("First 5 values:", vector[:5])


if __name__ == "__main__":
    test_embedding()