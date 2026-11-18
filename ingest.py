
from src.loader import RepositoryLoader
from src.chunker import CodeChunker
from src.vectorstore import VectorStore


def ingest_repository(
    repo_url: str,
    collection_name: str = "repository_code"
):
    print("Starting repository ingestion...")

    loader = RepositoryLoader()

    print("Cloning repository...")
    repo_path = loader.clone_repository(repo_url)

    try:
        # Step 1: Load repository files
        print("Loading repository files...")
        repository_data = loader.load_files(repo_path)

        print(f"Loaded {len(repository_data)} files.")

        if not repository_data:
            raise ValueError("No supported source files found.")

        # Step 2: Create code chunks
        print("Creating code chunks...")
        chunker = CodeChunker()
        chunks = chunker.chunk_repository(repository_data)

        print(f"Created {len(chunks)} chunks.")

        if not chunks:
            raise ValueError("No code chunks could be created.")

        # Step 3: Store chunks in the selected collection
        print("Generating embeddings and storing vectors...")
        vector_store = VectorStore(
            collection_name=collection_name
        )

        vector_store.add_chunks(chunks)

        total_chunks = vector_store.count()

        print(f"Stored {total_chunks} chunks in ChromaDB.")
        print("Repository ingestion completed successfully!")

        return {
            "files": len(repository_data),
            "chunks": len(chunks),
            "total_stored": total_chunks
        }

    finally:
        # Clean up cloned repository
        print("Cleaning up temporary repository...")
        loader.cleanup(repo_path)
        print("Cleanup completed.")


if __name__ == "__main__":
    repository_url = input(
        "Enter GitHub repository URL: "
    ).strip()

    if not repository_url:
        print("Repository URL cannot be empty.")
    else:
        ingest_repository(repository_url)
