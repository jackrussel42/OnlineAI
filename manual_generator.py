import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with your API key from environment variables
# Ensure your API key is named OPENAI_API_KEY in your .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="KI-Handbuch-Generator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("KI-Assistent für Bedienungsanleitungen 🤖")
st.write("Erstelle schnell und einfach Entwürfe für Abschnitte in Bedienungsanleitungen.")

# --- User Inputs ---
product_name = st.text_input("Produktname", placeholder="z.B. SmartHome Hub X")
topic_name = st.text_input("Thema des Abschnitts", placeholder="z.B. Installation und erste Inbetriebnahme")
additional_details = st.text_area("Zusätzliche Details oder Spezifikationen (optional)",
                                 placeholder="z.B. Schritte zur WLAN-Verbindung, Sicherheitshinweise, technische Daten.")

# --- Generation Logic ---
if st.button("Abschnitt generieren"):
    if not product_name or not topic_name:
        st.warning("Bitte gib den Produktnamen und das Thema des Abschnitts ein, um fortzufahren.")
    else:
        # Construct the prompt for the AI
        prompt_text = f"""
        Erstelle einen Abschnitt für eine Bedienungsanleitung.

        Produkt: {product_name}
        Thema des Abschnitts: {topic_name}
        """
        if additional_details:
            prompt_text += f"\nZusätzliche Details/Spezifikationen: {additional_details}"

        prompt_text += """
        Der Abschnitt sollte klar, prägnant, benutzerfreundlich und informativ sein.
        Verwende eine professionelle, leicht verständliche Sprache.
        Strukturiere den Text mit Überschriften, Listen und Absätzen.
        Integriere wichtige Sicherheitshinweise, falls relevant.
        """

        try:
            with st.spinner("Generiere Abschnitt... Dies kann einen Moment dauern."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # Or "gpt-3.5-turbo", "gpt-4" depending on your access and needs
                    messages=[
                        {"role": "system", "content": "Du bist ein erfahrener technischer Redakteur und hilfst dabei, klare und prägnante Bedienungsanleitungen zu erstellen."},
                        {"role": "user", "content": prompt_text}
                    ],
                    max_tokens=800, # Limit the length of the response
                    temperature=0.7 # Controls creativity. Lower means more predictable.
                )
            generated_text = response.choices[0].message.content

            st.subheader("Generierter Abschnitt:")
            st.markdown(generated_text) # Use markdown to render formatted text

            # Add copy to clipboard functionality
            st.code(generated_text, language='text') # Show the raw text for easy copying

            st.download_button(
                label="Text herunterladen",
                data=generated_text,
                file_name=f"Bedienungsanleitung_{product_name}_{topic_name}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
            st.info("Bitte stelle sicher, dass dein OpenAI API-Schlüssel korrekt ist und du ausreichend Guthaben hast.")