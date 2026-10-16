from app.core.config import get_settings
from app.services.ai.base import AIProvider
from app.services.ai.openai_compatible import OpenAICompatibleProvider


def get_ai_provider() -> AIProvider | None:
    provider = get_settings().ai_provider.casefold()
    if provider in {"", "none"}:
        return None
    if provider in {"openai", "openai_compatible"}:
        return OpenAICompatibleProvider()
    raise RuntimeError(f"Unsupported AI_PROVIDER: {provider}")
