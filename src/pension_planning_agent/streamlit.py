"""Streamlit UI helpers for the FIRE Pension Planning Agent."""

from __future__ import annotations

import uuid
from typing import Literal, TypedDict

import logfire
import streamlit as st
from google.genai import types
from loguru import logger

from pension_planning_agent.agent import runner, session_service

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire="never")


class ChatMessage(TypedDict):
    """Format of messages sent to the browser/API."""

    role: Literal["user", "model"]
    timestamp: str
    content: str


def display_message_part(message: dict) -> None:
    """
    Display a single message in the Streamlit UI.

    Args:
        message: Dictionary containing 'role' and 'content' keys
    """
    role = message.get("role", "user")
    content = message.get("content", "")

    if not content:
        logger.warning(f"Empty content for message with role: {role}")
        return

    if role == "system":
        with st.chat_message("system"):
            st.markdown(f"**System**: {content}")
    elif role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    elif role in ("assistant", "model"):
        with st.chat_message("assistant"):
            st.markdown(content)


async def run_agent(user_input: str) -> None:
    """
    Run the agent for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.

    Args:
        user_input: User's input text
    """
    try:
        # Get or create user ID and session ID
        if "user_id" not in st.session_state:
            st.session_state.user_id = "streamlit_user"

        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            # Create the session (await the async method)
            await session_service.create_session(
                app_name="fire_pension_agent",
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
            )
            logger.info(f"Created new session: {st.session_state.session_id}")

        # Create user message content
        new_message = types.Content(parts=[types.Part(text=user_input)])

        # Run the agent and collect response
        response_text = ""
        last_event = None

        for event in runner.run(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            new_message=new_message,
        ):
            last_event = event
            # Extract text from events
            if hasattr(event, "text") and event.text:
                response_text += event.text
            elif hasattr(event, "content") and event.content:
                # Handle Content object with parts
                content = event.content
                if hasattr(content, "parts"):
                    for part in content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text

        # If no text was extracted, use the last event
        if not response_text:
            response_text = (
                str(last_event) if last_event else "No response from the agent."
            )
            logger.warning(f"No text response extracted. Last event: {last_event}")

        # Store and display response
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
        st.markdown(response_text)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.exception(f"⛔️ {error_message}")
        st.error(error_message)

        # Store error in messages for context
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Error: {error_message}"}
        )
