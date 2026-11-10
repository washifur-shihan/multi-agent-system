import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    BaseSettings = object  # type: ignore
    SettingsConfigDict = None  # type: ignore


def _is_configured(val: str | None) -> bool:
    return bool(val and val.strip() and not val.strip().startswith("your_"))


class Settings(BaseSettings):  # type: ignore[misc]
    APP_NAME: str = os.getenv("APP_NAME", "Aurora Agent AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.1.0")

    # Mistral AI (Primary Free Tier)
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    MISTRAL_EMBEDDING_MODEL: str = os.getenv("MISTRAL_EMBEDDING_MODEL", "mistral-embed")
    MISTRAL_BASE_URL: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")

    # Groq (Optional Free Tier Alternative)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    # OpenAI (Optional Paid Tier)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "knowledge-files")

    # Vapi Voice
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
    def has_mistral(self) -> bool:
        return _is_configured(self.MISTRAL_API_KEY)

    @property
    def has_groq(self) -> bool:
        return _is_configured(self.GROQ_API_KEY)

    @property
    def has_openai(self) -> bool:
        return _is_configured(self.OPENAI_API_KEY)

    @property
    def has_llm(self) -> bool:
        return self.has_mistral or self.has_groq or self.has_openai

    @property
    def active_llm_provider(self) -> str:
        if self.has_mistral:
            return "mistral"
        if self.has_groq:
            return "groq"
        if self.has_openai:
            return "openai"
        return "standby"

    @property
    def active_llm_model(self) -> str:
        if self.has_mistral:
            return self.MISTRAL_MODEL
        if self.has_groq:
            return self.GROQ_MODEL
        if self.has_openai:
            return self.OPENAI_MODEL
        return "Mistral / LLM Standby"

    @property
    def has_supabase(self) -> bool:
        return _is_configured(self.SUPABASE_URL) and _is_configured(self.SUPABASE_SERVICE_ROLE_KEY)

    @property
    def has_vapi(self) -> bool:
        return _is_configured(self.VAPI_PUBLIC_KEY) and _is_configured(self.VAPI_ASSISTANT_ID)


settings = Settings()
