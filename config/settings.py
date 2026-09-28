from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "commerce-intelligence"
    app_env: str = "development"
    app_debug: bool = True

    database_url: str = (
        "postgresql+asyncpg://commerce:commerce_dev_password"
        "@localhost:5432/commerce_intelligence"
    )
    redis_url: str = "redis://localhost:6379/0"

    log_level: str = "INFO"

    ai_provider: str = "groq"

    openai_api_key: str | None = None

    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    browser_headless: bool = True
    browser_timeout_ms: int = 30000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()