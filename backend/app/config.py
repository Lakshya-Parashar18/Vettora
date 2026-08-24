from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    frontend_url: str = "http://localhost:5173"
    mongodb_uri: str = ""
    mongodb_database: str = "vettora"
    llm_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"
    llm_matching_model: str = "gemini-2.5-pro"
    llm_provider: str = "google"
    max_file_size_mb: int = 10
    max_jd_size_bytes: int = 100000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
