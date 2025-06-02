import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Streamlit App Configuration ---
# THIS MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="KI-Handbuch-Generator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Load environment variables from .env file
load_dotenv()

# Check if API key is loaded and configure genai
api_key_loaded = os.getenv("GOOGLE_API_KEY")
if not api_key_loaded:
    st.error("Fehler: Google API-Schlüssel nicht geladen. Bitte prüfen Sie die Secrets in Streamlit Cloud.")
    st.stop() # Stop the app if API key is not loaded
else:
    genai.configure(api_key=api_key_loaded)

# --- Initialize the Google Generative AI Model ---
# Based on the list, 'models/gemini-1.5-flash-latest' is a good choice for general text generation.
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest') # <--- CORRECTED MODEL NAME HERE
except Exception as e:
    st.error(f"Fehler beim Initialisieren des Gemini-Modells: {e}")
    st.info("Bitte überprüfen Sie den Modellnamen und die Verfügbarkeit in Ihrem Google Cloud Projekt.")
    st.stop() # Stop the app if the model cannot be initialized

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
                # Check if response.text exists and is not empty
                if hasattr(response, 'text') and response.text:
                    generated_text = response.text
                elif response and hasattr(response, 'candidates') and response.candidates:
                    # Fallback for some API responses that might put content in candidates
                    generated_text = response.candidates[0].text if hasattr(response.candidates[0], 'text') else "Kein Text generiert. Möglicherweise Inhaltsfilter."
                else:
                    generated_text = "Kein Text generiert. Möglicherweise ein API-Problem oder Inhaltsfilter."


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
            st.info("Bitte stelle sicher, dass dein Google API-Schlüssel korrekt ist, die Gemini API aktiviert ist und du ausreichend Guthaben hast. Auch Modellverfügbarkeit prüfen.")
