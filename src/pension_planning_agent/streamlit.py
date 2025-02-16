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


async def run_agent_with_streaming(user_input: str):
    """
    Run the agent with streaming text for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """

    # Run the agent in a stream
    try:
        async with fire_agent.run_stream(
            user_input,
            message_history=st.session_state.messages[
                :-1
            ],  # pass entire conversation so far
        ) as result:
            # We'll gather partial text to show incrementally
            partial_text = ""
            message_placeholder = st.empty()

            # Render partial text as it arrives
            async for chunk in result.stream_text(delta=True):
                partial_text += chunk
                message_placeholder.markdown(partial_text)

            # Now that the stream is finished, we have a final result.
            # Add new messages from this run, excluding user-prompt messages
            filtered_messages = [
                msg
                for msg in result.new_messages()
                if not (
                    hasattr(msg, "parts")
                    and any(part.part_kind == "user-prompt" for part in msg.parts)
                )
            ]
            st.session_state.messages.extend(filtered_messages)

            # Add the final response to the messages
            st.session_state.messages.append(
                ModelResponse(parts=[TextPart(content=partial_text)])
            )
    except Exception as e:
        logger.error(f"⛔️ An error occurred: {e}")
        st.error(f"An error occurred: {e}")
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=f"An error occurred: {e}")])
        )
