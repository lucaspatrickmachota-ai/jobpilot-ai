from typing import Any, Protocol


class AIProvider(Protocol):
    """Provider-neutral contract for completion, structured extraction and embeddings."""

    def complete(self, system_prompt: str, user_prompt: str) -> str: ...

    def extract_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...
