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

# --- TEMPORARY DEBUGGING: List available models ---
# This section will list the models available to your API key.
# After you get the correct model name, you will REPLACE this section
# with the actual model initialization.
st.subheader("Verfügbare Gemini Modelle für Ihr Projekt:")
try:
    found_gemini_pro_like_model = False
    for m in genai.list_models():
        # Only show models that support text generation via generateContent
        if 'generateContent' in m.supported_generation_methods:
            st.write(f"- `{m.name}` (Unterstützt: {m.supported_generation_methods})")
            if 'gemini-pro' in m.name or 'gemini-1.0-pro' in m.name:
                found_gemini_pro_like_model = True
    if not found_gemini_pro_like_model:
        st.warning("Kein 'gemini-pro' oder 'gemini-1.0-pro' Modell gefunden, das 'generateContent' unterstützt. Bitte überprüfen Sie Ihre Google Cloud Projektkonfiguration und API-Berechtigungen.")
except Exception as e:
    st.error(f"Fehler beim Auflisten der Modelle: {e}")
    st.info("Bitte stellen Sie sicher, dass die 'Generative Language API' in Ihrem Google Cloud Projekt aktiviert ist und das Abrechnungskonto verbunden ist.")

st.markdown("---") # Separator for clarity

# --- ORIGINAL APP CONTINUES BELOW ---
# IMPORTANT: After you get the correct model name from the list above,
# you will REMOVE the "TEMPORARY DEBUGGING" section (lines 20-35)
# and UNCOMMENT/CORRECT the line below with the exact model name you found.
# Example: model = genai.GenerativeModel('models/gemini-1.0-pro')
try:
    # Initialize the model that you found in the list above.
    # For now, we'll keep 'gemini-pro' as a placeholder, but you'll replace it.
    model = genai.GenerativeModel('gemini-pro')
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
