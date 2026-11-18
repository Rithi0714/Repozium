from src.vectorstore import VectorStore


def test_vectorstore():

    store = VectorStore()

    chunks = [
        {
            "file_path": "src/auth.py",
            "language": "python",
            "chunk_type": "method",
            "class_name": "AuthService",
            "function_name": "login",
            "start_line": 10,
            "end_line": 20,
            "chunk_id": 0,
            "content": (
                "def login(username, password):\n"
                "    authenticate the user using username and password\n"
                "    return authentication result"
            )
        },
        {
            "file_path": "src/database.py",
            "language": "python",
            "chunk_type": "function",
            "class_name": None,
            "function_name": "connect_database",
            "start_line": 5,
            "end_line": 15,
            "chunk_id": 0,
            "content": (
                "def connect_database():\n"
                "    connect to the MySQL database\n"
                "    return database connection"
            )
        },
        {
            "file_path": "src/email.py",
            "language": "python",
            "chunk_type": "function",
            "class_name": None,
            "function_name": "send_email",
            "start_line": 3,
            "end_line": 12,
            "chunk_id": 0,
            "content": (
                "def send_email(recipient, subject, message):\n"
                "    send an email notification to the recipient"
            )
        }
    ]

    store.add_chunks(chunks)

    print("Chunks stored:", store.count())

    results = store.search(
        "How does the application authenticate a user?",
        top_k=2
    )

    print("\nSearch results:")

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        print("\nDocument:")
        print(document)

        print("\nMetadata:")
        print(metadata)


if __name__ == "__main__":
    test_vectorstore()