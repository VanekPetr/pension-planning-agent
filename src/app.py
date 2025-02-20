from __future__ import annotations

import asyncio
import streamlit as st
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart
from pension_planning_agent.streamlit import (
    display_message_part,
    run_agent,
)


async def main():
    st.title("🔥 FIRE Agent")
    st.write(
        """
        Hej, jeg er en AI-agent, udviklet af [Penly](https://penly.dk), til at hjælpe dig med at få afklaring over hvornår du kan stoppe med at arbejde, eller gå ned i tid, mens du fortsat opretholder dit nuværende forbrugsniveau, eller eventuel gå op eller ned i forbrug.
        Du kan primært bruge mig til at find ud af, hvor meget du skal spare op, for at nå din såkaldte FIRE-mål.

        *FIRE står for Financial Independence Retire Early. Når vi taler om FIRE-planlægning i Penly, tænker vi på, hvordan vi kan få vores indtægter, opsparing og forbrug til at gå op i en højere enhed, over vores levetid, så vi kan leve det liv, vi ønsker.

        Mine beregninger er baseret på nogle simple forudsætninger. Grundlæggende vil jeg holde det helt simpelt i første omgang, men stadig realistisk i hele træskolængder. Du kan altid bygge videre på det, evt sammen med en rådgiver, hvis du vil gemme vores dialog og mine beregninger med bagvedliggende  forudsætninger, så du kan fortsætte med det senere. Men lad os komme i gang med din, muligvis, første FIRE-plan 🔥

        Det tager cirka 2 minutter at besvare mine spørgsmål, hvis du kender de begreber jeg bruger, og dine økonomiske tal. Hvis ikke du kender begreberne eller hvis du er i tvivl om det mindste, kan du bare spørge, og jeg skal nok forklare det i detaljer, med eksempler og det hele.

        Lad os komme i gang.
        Kan jeg få dig til fortælle lidt om dine FIRE tanker først?

        *Du må gerne skrive noget a la det Carina fra Penly har skrevet:*

        *Jeg hedder Carina, er 44 år. Jeg arbejder i Penly med marketing, kundeservice, og alt muligt andet. Min bruttoløn plus min arbejdsgiverpension er 45.000 kr. om måneden. Jeg betaler 10% til pension.Og jeg sætter pt 0 kr til side. Jeg kan godt leve med 22.000 kr. om måneden. Og vil gerne kunne stoppe eller gå ned i tid some 60 årig.*

        **Nu er det din tur:**
        """
    )

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display all messages from the conversation so far
    # Each message is either a ModelRequest or ModelResponse.
    # We iterate over their parts to decide how to display them.
    for msg in st.session_state.messages:
        if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
            for part in msg.parts:
                display_message_part(part)

    # Chat input for the user
    user_input = st.chat_input("Please write here.")

    if user_input:
        # We append a new request to the conversation explicitly
        st.session_state.messages.append(
            ModelRequest(parts=[UserPromptPart(content=user_input)])
        )

        # Display user prompt in the UI
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display the assistant's partial response while streaming
        with st.chat_message("assistant"):
            # Actually run the agent now, streaming the text
            await run_agent(user_input)


if __name__ == "__main__":
    asyncio.run(main())
