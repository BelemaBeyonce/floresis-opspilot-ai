import pytest

from app.services.chunking import chunk_text


def test_chunk_text_with_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=3,
    )

    assert chunks == [
        "ABCDEFGHIJ",
        "HIJKLMNOPQ",
        "OPQRSTUVWX",
        "VWXYZ",
    ]


def test_chunk_text_empty_string():
    chunks = chunk_text("")

    assert chunks == []


def test_chunk_text_normalizes_whitespace():
    text = "Floresis   processes\n\nenterprise    documents."

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=10,
    )

    assert chunks == [
        "Floresis processes enterprise documents."
    ]


def test_chunk_text_rejects_zero_chunk_size():
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than 0",
    ):
        chunk_text(
            "Hello world",
            chunk_size=0,
            overlap=0,
        )


def test_chunk_text_rejects_negative_overlap():
    with pytest.raises(
        ValueError,
        match="overlap cannot be negative",
    ):
        chunk_text(
            "Hello world",
            chunk_size=10,
            overlap=-1,
        )


def test_chunk_text_rejects_overlap_equal_to_chunk_size():
    with pytest.raises(
        ValueError,
        match="overlap must be smaller than chunk_size",
    ):
        chunk_text(
            "Hello world",
            chunk_size=10,
            overlap=10,
        )