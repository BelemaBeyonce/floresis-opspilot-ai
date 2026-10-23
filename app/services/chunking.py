def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Prefer word boundaries, but split long words
    when necessary to respect chunk_size.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # Prefer to end at a word boundary.
        if end < text_length and text[end] != " ":
            last_space = text.rfind(" ", start, end)

            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Keep some previous text as context.
        next_start = max(0, end - overlap)

        # Ensure we always move forward.
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks