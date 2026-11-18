
import time
import ollama


class LLMService:
    def __init__(self, model="qwen3:4b"):
        self.model = model

    def generate_answer(self, question, context):
        prompt = f"""
You are Repozium, an AI assistant that explains GitHub repositories.

Instructions:
1. Directly answer the user's question.
2. Trace the actual execution flow from controller to service to repository and database, only where supported by the context.
3. Explain what each method does and how data passes between layers.
4. Mention actual class names, method names, and file names.
5. Present the explanation in numbered steps.
6. Do not discuss source numbers or describe how the context was retrieved.
7. Do not invent missing implementation details.
8. If a layer or method is missing from the context, clearly say so.
9. End with a short summary of the complete flow.

REPOSITORY CONTEXT:
{context}

USER QUESTION:
{question}

Provide a complete and accurate answer.
"""

        print("\nGenerating answer using", self.model, "...")
        start_time = time.time()

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                think=False,
                options={
                    "temperature": 0.2,
                    "num_predict": 1000,
                    "num_ctx": 4096
                }
            )

            message = response["message"]
            answer = message.get("content", "").strip()

            elapsed = time.time() - start_time

            print("\nLLM PERFORMANCE")
            print("-------------------------")
            print("Model:", self.model)
            print("Thinking disabled: True")
            print("Stop reason:", response.get("done_reason"))
            print("Prompt tokens:", response.get("prompt_eval_count"))
            print("Generated tokens:", response.get("eval_count"))
            print(f"Generation time: {elapsed:.2f} seconds")
            print("-------------------------")

            if not answer:
                thinking = message.get("thinking", "")
                print("Thinking tokens/content length:", len(thinking))

                return (
                    "The model did not generate a final answer. "
                    "Please try asking the question differently."
                )

            if response.get("done_reason") == "length":
                answer += "\n\nNote: The response may be incomplete because the token limit was reached."

            return answer

        except Exception as error:
            print("LLM ERROR:", str(error))
            return "Sorry, I encountered an error while generating the answer."
