import logfire
import httpx
import streamlit as st
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from pension_planning_agent.system_prompt import system_prompt, final_message
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


async def fire_calculator(
    manedslon: float,
    alder: int,
    udbytte_ar: float,
    overskud_ar: float,
    pensionInd_ar: float,
    skat_percentage: float,
    udbytte_skat_percentage: float,
    forbrugsmal_md: float,
    frie_midler: float,
    holding_midler: float,
    rate_and_liv: float,
    nettoafkast: float,
    folkepensionsalder: int,
    fire_alder: int,
    folkepension: float,
) -> (dict, str):
    """
    Call the BusinessLogic API to calculate the pension plan.
    """
    skat_percentage = await convert_percentage_to_float(skat_percentage)
    udbytte_skat_percentage = await convert_percentage_to_float(udbytte_skat_percentage)
    nettoafkast = await convert_percentage_to_float(nettoafkast)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.businesslogic.online/execute",
            headers={
                "X-Auth-Token": settings.BUSINESSLOGIC_TOKEN,
                "Content-Type": "application/json",
            },
            json={
                "manedslon": manedslon,
                "alder": alder,
                "udbytte_ar": udbytte_ar,
                "overskud_ar": overskud_ar,
                "pensionInd_ar": pensionInd_ar,
                "skat_percentage": skat_percentage,
                "udbytte_skat_percentage": udbytte_skat_percentage,
                "forbrugsmal_md": forbrugsmal_md,
                "frie_midler": frie_midler,
                "holding_midler": holding_midler,
                "rate_and_liv": rate_and_liv,
                "nettoafkast": nettoafkast,
                "folkepensionsalder": folkepensionsalder,
                "fire_alder": fire_alder,
                "folkepension": folkepension,
            },
        )
        return response.json(), final_message


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
    text_2 = "manedslon=75700, alder=52, udbytte_ar=0, overskud_ar=0, pensionInd_ar=85000, skat_percentage=33, udbytte_skat_percentage=27, forbrugsmal_md=34100, frie_midler=935000, holding_midler=0, rate_and_liv=4190000, nettoafkast=3.5, folkepensionsalder=70, fire_alder=62, folkepension=86000"
    result = await fire_agent.run(text_2)
    print(result.data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
