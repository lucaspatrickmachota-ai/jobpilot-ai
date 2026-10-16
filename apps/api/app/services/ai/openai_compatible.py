"""OpenAI-compatible HTTP adapter; API credentials are read only from environment settings."""
import json
from typing import Any

import httpx

from app.core.config import get_settings


class OpenAICompatibleProvider:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.ai_api_key or not settings.ai_model:
            raise RuntimeError("AI_API_KEY and AI_MODEL are required for the configured AI provider")
        self.base_url = settings.ai_base_url.rstrip("/")
        self.api_key = settings.ai_api_key
        self.model = settings.ai_model
        self.embedding_model = settings.ai_embedding_model
        self.timeout = settings.ai_timeout_seconds

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(f"{self.base_url}{path}", json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("AI provider returned an invalid response")
        return data

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        data = self._post("/chat/completions", {"model": self.model, "messages": [
            {"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0})
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("AI provider returned no completion content") from exc
        if not isinstance(content, str):
            raise ValueError("AI provider completion content must be text")
        return content

    def extract_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        data = self._post("/chat/completions", {"model": self.model, "messages": [
            {"role": "system", "content": system_prompt + "\nReturn JSON conforming to this schema:\n" + json.dumps(schema)},
            {"role": "user", "content": user_prompt}],
            "temperature": 0, "response_format": {"type": "json_object"}})
        try:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("AI provider returned invalid structured JSON") from exc
        if not isinstance(parsed, dict):
            raise ValueError("AI provider structured output must be a JSON object")
        return parsed

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        data = self._post("/embeddings", {"model": self.embedding_model, "input": texts})
        try:
            vectors = [item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])]
        except (KeyError, TypeError) as exc:
            raise ValueError("AI provider returned invalid embeddings") from exc
        if len(vectors) != len(texts) or any(not isinstance(vector, list) for vector in vectors):
            raise ValueError("AI provider returned an unexpected embedding count")
        return vectors
