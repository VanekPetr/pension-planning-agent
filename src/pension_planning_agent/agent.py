"""FIRE Pension Planning Agent using Google ADK and OpenRouter."""

from __future__ import annotations

import httpx
import logfire
from google.adk import Runner
from google.adk.agents import Agent
from google.adk.models import LiteLlm
from google.adk.sessions import InMemorySessionService
from loguru import logger
from pydantic import ValidationError

from pension_planning_agent.schemas import FireCalculatorInput
from pension_planning_agent.system_prompt import system_prompt
from settings import settings

logfire.configure(send_to_logfire="if-token-present")


async def convert_percentage_to_float(percentage: float) -> float:
    """
    Convert a percentage string to a float.
    """
    return percentage / 100 if percentage > 1 else percentage


def generate_final_message(response: dict | None) -> str:
    """Generate the final message with calculation results.

    Args:
        response: API response containing calculation results

    Returns:
        str: Formatted message for the user
    """
    if not response or not isinstance(response, dict):
        return "Agenten kunne ikke finde nogle informationer."

    opsparing_ar = response.get("opsparing_ar")
    result = response.get("result")

    if opsparing_ar is None or result is None:
        return "Agenten kunne ikke beregne pensionsplanen. Prøv igen med andre værdier."

    return f"""
Hvis du sparer {opsparing_ar:,.0f} kr. om året i løbet af dine arbejdsår, vil din nettofortjeneste i frie midler ved din alder 95 være {result:,.0f} kr.

Hvis beløbet er positivt, er du på rette vej. Hvis det er negativt, skal du enten spare mere op eller reducere dit forventede forbrug.

Vil du gerne gemme dine oplysninger, så du kan ændre på forudsætninger og lave flere beregninger? Det kræver, at du opretter en gratis Penly profil eller logge ind med din Penly profil, hvis du allerede har en Penly profil.
- [Opret Profil](https://penly.dk/opret?)
- [Log ind - hvis du har en profil](https://auth.neway.dk/realms/neway/protocol/openid-connect/auth?client_id=penly-frontend&redirect_uri=https%3A%2F%2Fpenly.dk%2F%2Fmit-penly%2Fpension&state=e8043e15-e8cc-499d-a1c3-514b26c39c8d&response_mode=fragment&response_type=code&scope=openid&nonce=24c54004-277b-4db4-8c96-98aa0d7e6aee)

Vil du fortsætte dialogen med en Penly rådgiver, kan du booke en gratis 15-minutters møde [her](https://penly.dk/opret?):
Ved mødet kan du også få en EXCEL-fil, hvor du selv kan lege videre og præcisere din FIRE-plan.
Rådgiveren vil også kunne fortælle dig, hvis der er ting, du bør overveje for at optimere din op- og nedsparingsplan.
"""


async def fire_calculator(
    manedslon: float,
    alder: int,
    pensionInd_ar: float,
    skat_percentage: float,
    forbrugsmal_md: float,
    frie_midler: float,
    holding_midler: float,
    rate_and_liv: float,
    fire_alder: int,
) -> str:
    """
    Call the BusinessLogic API to calculate the pension plan.

    Args:
        manedslon: Monthly salary
        alder: Current age
        pensionInd_ar: Annual pension contributions
        skat_percentage: Tax percentage after AMB
        forbrugsmal_md: Monthly consumption target
        frie_midler: Initial free funds balance
        holding_midler: Initial holding balance
        rate_and_liv: Rate and annuity pension
        fire_alder: Target FIRE age

    Returns:
        str: Final message with pension plan calculation results
    """
    # Validate inputs using Pydantic
    try:
        calculator_input = FireCalculatorInput(
            manedslon=manedslon,
            alder=alder,
            pensionInd_ar=pensionInd_ar,
            skat_percentage=skat_percentage,
            forbrugsmal_md=forbrugsmal_md,
            frie_midler=frie_midler,
            holding_midler=holding_midler,
            rate_and_liv=rate_and_liv,
            fire_alder=fire_alder,
        )
    except ValidationError as e:
        error_msg = "Invalid input parameters:\n"
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_msg += f"- {field}: {error['msg']}\n"
        logger.error(f"Validation error: {error_msg}")
        return error_msg

    skat_percentage = await convert_percentage_to_float(
        calculator_input.skat_percentage
    )
    folkepensionsalder = 70  # TODO: Calculate based on birth year

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.businesslogic.online/execute",
                headers={
                    "X-Auth-Token": settings.BUSINESSLOGIC_TOKEN,
                    "Content-Type": "application/json",
                },
                json={
                    "manedslon": calculator_input.manedslon,
                    "alder": calculator_input.alder,
                    "pensionInd_ar": calculator_input.pensionInd_ar,
                    "skat_percentage": skat_percentage,
                    "forbrugsmal_md": calculator_input.forbrugsmal_md,
                    "frie_midler": calculator_input.frie_midler,
                    "holding_midler": calculator_input.holding_midler,
                    "rate_and_liv": calculator_input.rate_and_liv,
                    "folkepensionsalder": folkepensionsalder,
                    "fire_alder": calculator_input.fire_alder,
                },
            )
            response.raise_for_status()
            return generate_final_message(response.json())
    except httpx.TimeoutException:
        error_msg = "Request timed out. Please try again later."
        logger.error(error_msg)
        return error_msg
    except httpx.HTTPStatusError as e:
        error_msg = f"API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return (
            f"Failed to calculate pension plan. Please check your inputs and try again."
        )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return "An unexpected error occurred. Please try again later."


# Get API key from environment or Streamlit secrets
try:
    import streamlit as st

    api_key = (
        settings.OPEN_ROUTER_API_KEY
        if settings.OPEN_ROUTER_API_KEY != "open-key"
        else st.secrets.get("OPEN_ROUTER_API_KEY")
    )
except Exception:
    api_key = settings.OPEN_ROUTER_API_KEY


# Configure LiteLLM to use OpenRouter
model = LiteLlm(
    model=settings.LLM_MODEL,
    api_key=api_key,
    api_base="https://openrouter.ai/api/v1",
    # Optional: Add reasoning parameters for thinking models
    extra_params={"reasoning_effort": "high"},  # For reasoning models
)

fire_agent = Agent(
    name="fire_pension_agent",
    model=model,
    instruction=system_prompt,
    description="AI agent for personalized pension planning, offering savings projections, retirement income analysis, and contribution optimization.",
    tools=[fire_calculator],
)

# Create session service and runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="fire_pension_agent", agent=fire_agent, session_service=session_service
)


async def main():
    from google.genai import types

    text_1 = """"
            Jeg hedder Carina, er 44 år. Jeg arbejder i Penly med marketing, kundeservice, og alt muligt andet. Min bruttoløn plus min arbejdsgiverpension er 45.000 kr. om måneden. Jeg betaler 10% til pension.
            Jeg får cirka 25.000 kr. udbetalt hver måned efter skat og indbetaling til pensioner. Og jeg sætter pt 0 kr til side.
            Men jeg kan godt sætte 3.000 kr. til side hver måned. Jeg kan godt leve med 22.000 kr. om måneden. Og vil gerne kunne stoppe eller gå ned i tid some 60 årig.

            PLEASE REPLY IN ENGLISH.
        """
    text_2 = "manedslon=75700, alder=52, pensionInd_ar=85000, skat_percentage=33, forbrugsmal_md=34100, frie_midler=935000, holding_midler=0, rate_and_liv=4190000,fire_alder=62"

    # Create a session first (await the async method)
    user_id = "test_user"
    session_id = "test_session"
    app_name = "fire_pension_agent"
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    # Create user message content
    new_message = types.Content(parts=[types.Part(text=text_2)])

    # Run the agent
    result_text = ""
    last_event = None
    for event in runner.run(
        user_id=user_id, session_id=session_id, new_message=new_message
    ):
        last_event = event
        # Process events to extract the response
        if hasattr(event, "text") and event.text:
            result_text += event.text
        elif hasattr(event, "content") and event.content:
            # Handle Content object with parts
            content = event.content
            if hasattr(content, "parts"):
                for part in content.parts:
                    if hasattr(part, "text") and part.text:
                        result_text += part.text

    print(
        result_text
        if result_text
        else (str(last_event) if last_event else "No response")
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
