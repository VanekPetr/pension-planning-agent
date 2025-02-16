from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    NAME: str = "Pension Planning Agent"
    OPEN_ROUTER_API_KEY: str = "open-key"
    LLM_MODEL: str = "google/gemini-2.0-flash-001"
    BUSINESSLOGIC_TOKEN: str = "businesslogic-token"


settings = Settings()
