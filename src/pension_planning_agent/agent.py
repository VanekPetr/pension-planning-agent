import logfire
import httpx
import streamlit as st
from pydantic_ai import Agent, RunContext
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


async def convert_percentage_to_float(percentage: float) -> float:
    """
    Convert a percentage string to a float.
    """
    return percentage / 100 if percentage > 1 else percentage


def generate_final_message(response: dict) -> str:
    if response:
        return f"""
            Hvis du sparer {response["opsparing_ar"]} kr. om året i løbet af dine arbejdsår, vil din nettofortjeneste i frie midler ved din alder 95 være {response["result"]} kr.

            Hvis beløbet er positivt, er du på rette vej. Hvis det er negativt, skal du enten spare mere op eller reducere dit forventede forbrug.

            Vil du gerne gemme dine oplysninger, så du kan ændre på forudsætninger og lave flere beregninger? Det kræver, at du opretter en gratis Penly profil eller logge ind med din Penly profil, hvis du allerede har en Penly profil.
            - [Opret Profil](https://penly.dk/opret?)
            - [Log ind - hvis du har en profil](https://auth.neway.dk/realms/neway/protocol/openid-connect/auth?client_id=penly-frontend&redirect_uri=https%3A%2F%2Fpenly.dk%2F%2Fmit-penly%2Fpension&state=e8043e15-e8cc-499d-a1c3-514b26c39c8d&response_mode=fragment&response_type=code&scope=openid&nonce=24c54004-277b-4db4-8c96-98aa0d7e6aee)

            Vil du fortsætte dialogen med en Penly rådgiver, kan du booke en gratis 15-minutters møde [her](https://penly.dk/opret?):
            Ved mødet kan du også få en EXCEL-fil, hvor du selv kan lege videre og præcisere din FIRE-plan.
            Rådgiveren vil også kunne fortælle dig, hvis der er ting, du bør overveje for at optimere din op- og nedsparingsplan.
        """
    else:
        return "Agenten kunne ikke finde nogle informationer."


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
    """
    skat_percentage = await convert_percentage_to_float(skat_percentage)
    folkepensionsalder = 70  # TODO calculate this

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.businesslogic.online/execute",
            headers={
                "X-Auth-Token": settings.BUSINESSLOGIC_TOKEN,
                "Content-Type": "application/json",
            },
            json={
                "manedslon": manedslon,
                "alder": alder,
                "pensionInd_ar": pensionInd_ar,
                "skat_percentage": skat_percentage,
                "forbrugsmal_md": forbrugsmal_md,
                "frie_midler": frie_midler,
                "holding_midler": holding_midler,
                "rate_and_liv": rate_and_liv,
                "folkepensionsalder": folkepensionsalder,
                "fire_alder": fire_alder,
            },
        )

        return generate_final_message(response.json())


fire_agent = Agent(
    model=model, system_prompt=system_prompt, retries=2, tools=[fire_calculator]
)


async def main():
    text_1 = """"
            Jeg hedder Carina, er 44 år. Jeg arbejder i Penly med marketing, kundeservice, og alt muligt andet. Min bruttoløn plus min arbejdsgiverpension er 45.000 kr. om måneden. Jeg betaler 10% til pension.
            Jeg får cirka 25.000 kr. udbetalt hver måned efter skat og indbetaling til pensioner. Og jeg sætter pt 0 kr til side.
            Men jeg kan godt sætte 3.000 kr. til side hver måned. Jeg kan godt leve med 22.000 kr. om måneden. Og vil gerne kunne stoppe eller gå ned i tid some 60 årig.

            PLEASE REPLY IN ENGLISH.
        """
    text_2 = "manedslon=75700, alder=52, pensionInd_ar=85000, skat_percentage=33, forbrugsmal_md=34100, frie_midler=935000, holding_midler=0, rate_and_liv=4190000,fire_alder=62"
    result = await fire_agent.run(text_2)
    print(result.data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
