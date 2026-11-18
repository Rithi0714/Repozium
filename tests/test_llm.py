from src.llm import LLMService


def test_llm():

    llm = LLMService()

    context = """
File: src/CandidateService.java

Class: CandidateService

Function: updateStatus

Code:

public void updateStatus(Long candidateId, CandidateStatus status) {
    Candidate candidate = candidateRepository.findById(candidateId);
    candidate.setStatus(status);
    candidateRepository.save(candidate);
}
"""

    question = "Where is the candidate status updated?"

    answer = llm.generate_answer(
        question=question,
        context=context
    )

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    test_llm()