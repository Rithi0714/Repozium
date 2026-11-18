from src.retriever import Retriever


def test_retriever():

    retriever = Retriever(top_k=5)

    query = "Where is candidate status updated?"

    results = retriever.retrieve(query)

    print("\nRetrieved chunks:", len(results))

    for index, result in enumerate(results, start=1):

        print("\n" + "=" * 60)

        print(f"Result {index}")

        print("=" * 60)

        print("\nFile:")
        print(result["metadata"].get("file_path"))

        print("\nClass:")
        print(result["metadata"].get("class_name"))

        print("\nFunction:")
        print(result["metadata"].get("function_name"))

        print("\nDistance:")
        print(result["distance"])

        print("\nContent:")
        print(result["content"])


if __name__ == "__main__":
    test_retriever()