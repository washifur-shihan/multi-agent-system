import re


def normalize_whitespace(text: str) -> str:
    """Collapse excessive whitespace while preserving paragraph breaks."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 750, overlap: int = 120) -> list[str]:
    """Split text into overlapping chunks along natural sentence/paragraph boundaries."""
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            # Try breaking at paragraph, newline, or sentence boundary
            for sep in ("\n\n", "\n", ". ", "? ", "! ", " "):
                boundary = cleaned.rfind(sep, start + int(chunk_size * 0.5), end)
                if boundary != -1:
                    end = boundary + len(sep)
                    break

        segment = cleaned[start:end].strip()
        if segment:
            chunks.append(segment)

        if end >= length:
            break

        start = max(start + 1, end - overlap)

    return chunks

