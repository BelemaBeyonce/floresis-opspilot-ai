import json
import ollama

LLM_MODEL = "llama3.2:1b"

NO_ANSWER = (
    "The uploaded documents do not contain enough "
    "information to answer this question."
)


def generate_answer(question: str, evidence: list[dict]) -> dict:
    """
    Generate an answer and indicate whether the
    retrieved evidence supports it.
    """

    if not evidence:
        return {
            "answer": NO_ANSWER,
            "supported": False,
        }

    context = "\n\n".join(
        f"[Source {index}] {item['content']}"
        for index, item in enumerate(evidence, start=1)
    )

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Floresis OpsPilot AI. "
                    "Answer only from the provided document excerpts. "
                    "Return a JSON object with exactly two fields: "
                    "'answer' (string) and 'supported' (boolean). "
                    "Set supported to true only when the excerpts "
                    "directly answer the question. "
                    "Otherwise set supported to false and use "
                    f"this exact answer: {NO_ANSWER} "
                    "When supported, keep the answer concise "
                    "and cite the source as [Source 1]."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Document excerpts:\n{context}\n\n"
                    f"Question: {question}"
                ),
            },
        ],
        format="json",
        options={
            "temperature": 0,
            "num_predict": 180,
        },
    )

    try:
        result = json.loads(response["message"]["content"])

        if result.get("supported") is not True:
            return {
                "answer": NO_ANSWER,
                "supported": False,
            }

        answer_text = result.get("answer")

        if not isinstance(answer_text, str) or not answer_text.strip():
            return {
                "answer": NO_ANSWER,
                "supported": False,
            }

        return {
            "answer": answer_text.strip(),
            "supported": True,
        }

    except (json.JSONDecodeError, TypeError, KeyError):
        return {
            "answer": NO_ANSWER,
            "supported": False,
        }