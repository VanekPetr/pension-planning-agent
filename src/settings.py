from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    NAME: str = "Pension Planning Agent"
    OPEN_ROUTER_API_KEY: str = "open-key"
    LLM_MODEL: str = "openrouter/google/gemini-2.5-flash"
    BUSINESSLOGIC_TOKEN: str = (
        "businesslogic-token"  # Please contact petrr.vanekk@gmail.com for the token
    )


settings = Settings()
