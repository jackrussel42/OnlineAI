import streamlit as st
import google.generativeai as genai # This is the new import
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Google Generative AI client with your API key from environment variables
# Ensure your API key is named GOOGLE_API_KEY in your .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model instance
# You might choose a specific model like 'gemini-pro' or 'gemini-1.5-pro'
# Check Google's API documentation for available models.
model = genai.GenerativeModel('gemini-pro')
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
                response = model.generate_content(
                    [{"role": "system", "parts": ["Du bist ein erfahrener technischer Redakteur und hilfst dabei, klare und prägnante Bedienungsanleitungen zu erstellen."]},
                     {"role": "user", "parts": [prompt_text]}],
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=800, # Limit the length of the response
                        temperature=0.7 # Controls creativity. Lower means more predictable.
                    )
                )
            generated_text = response.text # Google Gemini response access

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
