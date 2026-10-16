from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://jobpilot:jobpilot_dev_only@localhost:5432/jobpilot"
    jwt_secret: str = "development-only-change-me"
    access_token_minutes: int = 30
    max_resume_size_mb: int = 10
    ai_provider: str = "none"
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_base_url: str = "https://api.openai.com/v1"
    ai_embedding_model: str = "text-embedding-3-small"
    ai_timeout_seconds: float = 30.0
    embedding_dimensions: int = 1536
    match_weight_skills: float = 0.50
    match_weight_experience: float = 0.30
    match_weight_education: float = 0.10
    match_weight_languages: float = 0.10

    @model_validator(mode="after")
    def validate_configuration(self) -> "Settings":
        weights = (self.match_weight_skills, self.match_weight_experience, self.match_weight_education, self.match_weight_languages)
        if any(weight < 0 for weight in weights) or abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError("MATCH_WEIGHT_* settings must be non-negative and sum to 1.0")
        if self.max_resume_size_mb < 1:
            raise ValueError("MAX_RESUME_SIZE_MB must be at least 1")
        if self.embedding_dimensions != 1536:
            raise ValueError("This migration uses 1536-dimensional vectors; EMBEDDING_DIMENSIONS must equal 1536")
        if self.app_env.casefold() == "production":
            if self.jwt_secret == "development-only-change-me" or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be a unique secret of at least 32 characters in production")
            if not self.cors_origins or any("localhost" in origin for origin in self.cors_origins):
                raise ValueError("CORS_ORIGINS must contain only the intended production origins")
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
