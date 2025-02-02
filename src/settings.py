from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    NAME: str = "Pension Planning Agent"
    OPEN_ROUTER_API_KEY: str = "open-key"
    LLM_MODEL: str = "google/gemini-2.0-flash-exp:free"

    # NOT NEEDED
    GITHUB_TOKEN: str = "github-token"
    API_BEARER_TOKEN: str = "api-token"
    SUPABASE_URL: str = "https://api.supabase.io"
    SUPABASE_SERVICE_KEY: str = "supabase-key"


settings = Settings()
