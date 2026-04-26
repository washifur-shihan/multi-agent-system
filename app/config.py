from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_BUCKET: str = "knowledge-files"
    OPENAI_API_KEY: str
    VAPI_API_KEY: str | None = None
    ELEVENLABS_API_KEY: str | None = None
    VAPI_PUBLIC_KEY: str | None = None
    VAPI_ASSISTANT_ID: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()