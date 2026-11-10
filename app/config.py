import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    BaseSettings = object  # type: ignore
    SettingsConfigDict = None  # type: ignore


class Settings(BaseSettings):  # type: ignore[misc]
    APP_NAME: str = os.getenv("APP_NAME", "Aurora Agent AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "knowledge-files")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    VAPI_API_KEY: str | None = os.getenv("VAPI_API_KEY")
    ELEVENLABS_API_KEY: str | None = os.getenv("ELEVENLABS_API_KEY")
    VAPI_PUBLIC_KEY: str | None = os.getenv("VAPI_PUBLIC_KEY")
    VAPI_ASSISTANT_ID: str | None = os.getenv("VAPI_ASSISTANT_ID")

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

    @property
    def has_supabase(self) -> bool:
        return bool(
            self.SUPABASE_URL
            and self.SUPABASE_SERVICE_ROLE_KEY
            and not self.SUPABASE_URL.startswith("your_")
            and not self.SUPABASE_SERVICE_ROLE_KEY.startswith("your_")
        )

    @property
    def has_openai(self) -> bool:
        return bool(
            self.OPENAI_API_KEY
            and not self.OPENAI_API_KEY.startswith("your_")
        )

    @property
    def has_vapi(self) -> bool:
        return bool(
            self.VAPI_PUBLIC_KEY
            and self.VAPI_ASSISTANT_ID
            and not self.VAPI_PUBLIC_KEY.startswith("your_")
            and not self.VAPI_ASSISTANT_ID.startswith("your_")
        )


settings = Settings()
