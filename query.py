
import time

from src.retriever import Retriever
from src.llm import LLMService


def build_context(retrieved_chunks):
    """
    Build structured context from retrieved repository chunks.
    """

    context_parts = []
    seen_chunks = set()

    for index, chunk in enumerate(retrieved_chunks, start=1):

        metadata = chunk.get("metadata", {})
        content = chunk.get("content", "")

        if not content or not content.strip():
            continue

        normalized_content = content.strip()

        if normalized_content in seen_chunks:
            continue

        seen_chunks.add(normalized_content)

        file_path = metadata.get("file_path", "Unknown file")
        language = metadata.get("language", "Unknown")
        chunk_type = metadata.get("chunk_type", "Unknown")
        class_name = metadata.get("class_name") or "Not specified"
        function_name = metadata.get("function_name") or "Not specified"
        start_line = metadata.get("start_line", "Unknown")
        end_line = metadata.get("end_line", "Unknown")

        context_parts.append(
            f"""
SOURCE {index}
File: {file_path}
Language: {language}
Type: {chunk_type}
Class: {class_name}
Function: {function_name}
Lines: {start_line}-{end_line}

Code:
{content}

----------------------------------------
"""
        )

    return "\n".join(context_parts)


def answer_question(
    question: str,
    collection_name: str = "repository_code"
):
    """
    Retrieve repository code and generate an AI answer.
    """

    if not question or not question.strip():
        return "Please enter a valid question."

    print("\n--- REPOZIUM PERFORMANCE REPORT ---")

    # Step 1: Initialize retriever.
    start = time.time()

    retriever = Retriever(
        top_k=10,
        collection_name=collection_name
    )

    print(
        f"Retriever initialization: "
        f"{time.time() - start:.2f} seconds"
    )

    # Step 2: Retrieve relevant chunks.
    start = time.time()

    retrieved_chunks = retriever.retrieve(question)

    print(
        f"Vector search: "
        f"{time.time() - start:.2f} seconds"
    )

    if not retrieved_chunks:
        return (
            "I couldn't find relevant information "
            "in the indexed repository."
        )

    print(f"Retrieved chunks: {len(retrieved_chunks)}")

    print("\nRetrieved files:")

    for chunk in retrieved_chunks:
        print(
            f"- {chunk['file_path']} "
            f"(distance: {chunk['distance']})"
        )

    # Step 3: Build context.
    start = time.time()

    context = build_context(retrieved_chunks)

    print(
        f"\nContext building: "
        f"{time.time() - start:.2f} seconds"
    )

    print(f"Context size: {len(context)} characters")

    # Step 4: Initialize LLM.
    start = time.time()

    llm = LLMService()

    print(
        f"LLM initialization: "
        f"{time.time() - start:.2f} seconds"
    )

    # Step 5: Generate answer.
    start = time.time()

    answer = llm.generate_answer(
        question=question,
        context=context
    )

    print(
        f"LLM generation: "
        f"{time.time() - start:.2f} seconds"
    )

    print("-----------------------------------\n")

    return answer


def main():

    print("\n" + "=" * 50)
    print("                 REPOZIUM")
    print("          AI Repository Assistant")
    print("=" * 50)

    print("\nAsk a question about the repository.")
    print("Type 'exit' to quit.")

    while True:

        question = input("\n> ").strip()

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break

        try:
            start = time.time()

            answer = answer_question(question)

            print("\nRepozium:")
            print(answer)

            print(
                f"\nTotal processing time: "
                f"{time.time() - start:.2f} seconds"
            )

        except Exception as error:
            print("\nAn error occurred:")
            print(f"Details: {error}")


if __name__ == "__main__":
    main()
