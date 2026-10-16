import re


def chunk_text(text: str, *, max_chars: int = 900, overlap: int = 120) -> list[str]:
    """Split extracted resume text into bounded overlapping chunks without empty fragments."""
    if max_chars < 100 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Require max_chars >= 100 and 0 <= overlap < max_chars")
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    if not normalized:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks
