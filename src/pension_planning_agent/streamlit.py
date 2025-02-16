from __future__ import annotations

import logfire
import streamlit as st
from typing import Literal, TypedDict
from pydantic_ai.messages import ModelResponse, TextPart
from pension_planning_agent.agent import fire_agent
from loguru import logger

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire="never")


class ChatMessage(TypedDict):
    """Format of messages sent to the browser/API."""

    role: Literal["user", "model"]
    timestamp: str
    content: str


def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # system-prompt
    if part.part_kind == "system-prompt":
        with st.chat_message("system"):
            st.markdown(f"**System**: {part.content}")
    # user-prompt
    elif part.part_kind == "user-prompt":
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == "text":
        with st.chat_message("assistant"):
            st.markdown(part.content)


async def run_agent(user_input: str):
    """
    Run the agent without streaming text for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """

    try:
        result = await fire_agent.run(
            user_input, message_history=st.session_state.messages[:-1]
        )

        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=result.data)])
        )
        st.markdown(result.data)

    except Exception as e:
        logger.error(f"⛔️ An error occurred: {e}")
        st.error(f"An error occurred: {e}")
