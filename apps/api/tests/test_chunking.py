import pytest

from app.services.chunking import chunk_text


def test_chunking_preserves_content_with_overlap() -> None:
    text = "word " * 700
    chunks = chunk_text(text, max_chars=300, overlap=40)
    assert len(chunks) > 1
    assert all(0 < len(chunk) <= 300 for chunk in chunks)
    assert "word" in chunks[0] and "word" in chunks[-1]


def test_chunking_empty_and_invalid_settings() -> None:
    assert chunk_text("   ") == []
    with pytest.raises(ValueError):
        chunk_text("some text", max_chars=100, overlap=100)
