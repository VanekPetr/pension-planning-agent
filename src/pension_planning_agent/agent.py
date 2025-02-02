import logfire
import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from pension_planning_agent.system_prompt import system_prompt
from settings import settings

logfire.configure(send_to_logfire="if-token-present")
model = OpenAIModel(
    model_name=settings.LLM_MODEL,
    base_url="https://openrouter.ai/api/v1",
    api_key=(
        settings.OPEN_ROUTER_API_KEY
        if settings.OPEN_ROUTER_API_KEY != "open-key"
        else st.secrets["OPEN_ROUTER_API_KEY"]
    ),
)

agent = Agent(model=model, system_prompt=system_prompt, retries=2)

if __name__ == "__main__":
    result = agent.run_sync("Good, thank you. Can you help me?")
    print(result.data)
