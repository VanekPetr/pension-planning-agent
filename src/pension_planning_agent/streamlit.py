from __future__ import annotations

import logfire
import streamlit as st
from typing import Literal, TypedDict
from pension_planning_agent.agent import runner
from loguru import logger

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire="never")


class ChatMessage(TypedDict):
    """Format of messages sent to the browser/API."""

    role: Literal["user", "model"]
    timestamp: str
    content: str


def display_message_part(message: dict):
    """
    Display a single message in the Streamlit UI.
    """
    role = message.get("role", "user")
    content = message.get("content", "")

    if role == "system":
        with st.chat_message("system"):
            st.markdown(f"**System**: {content}")
    elif role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    elif role == "assistant" or role == "model":
        with st.chat_message("assistant"):
            st.markdown(content)


async def run_agent(user_input: str):
    """
    Run the agent for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """
    from google.genai import types
    from pension_planning_agent.agent import session_service

    try:
        # Get or create user ID and session ID
        if "user_id" not in st.session_state:
            st.session_state.user_id = "streamlit_user"

        if "session_id" not in st.session_state:
            import uuid

            st.session_state.session_id = str(uuid.uuid4())
            # Create the session (await the async method)
            await session_service.create_session(
                app_name="fire_pension_agent",
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
            )

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

        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
        st.markdown(response_text)

    except Exception as e:
        logger.error(f"⛔️ An error occurred: {e}")
        st.error(f"An error occurred: {e}")
        st.markdown("Error in the agent.")
