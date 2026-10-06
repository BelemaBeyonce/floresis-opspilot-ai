import re

from app.models import Document


def score(question: str, text: str) -> int:
    terms = set(
        re.findall(
            r"[a-zA-Z]{3,}",
            question.lower(),
        )
    )

    body = text.lower()

    return sum(
        body.count(term)
        for term in terms
    )


def answer(
    question: str,
    documents: list[Document],
):
    ranked = sorted(
        (
            (
                score(
                    question,
                    document.title + " " + document.content,
                ),
                document,
            )
            for document in documents
        ),
        reverse=True,
        key=lambda item: item[0],
    )

    chosen = [
        document
        for relevance_score, document in ranked
        if relevance_score > 0
    ][:3]

    if not chosen:
        return (
            "No grounded evidence was found. "
            "Add relevant documents before relying on an answer.",
            [],
        )

    snippets = []

    for document in chosen:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            document.content,
        )

        best_sentence = (
            max(
                sentences,
                key=lambda sentence: score(
                    question,
                    sentence,
                ),
            )
            if sentences
            else document.content[:300]
        )

        snippets.append(
            f"{best_sentence.strip()} [{document.id}]"
        )

    response = (
        "Evidence-backed synthesis: "
        + " ".join(snippets)
    )

    citations = [
        {
            "document_id": document.id,
            "title": document.title,
        }
        for document in chosen
    ]

    return response, citations