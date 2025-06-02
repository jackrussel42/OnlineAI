import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Streamlit App Configuration ---
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
    st.stop()
else:
    genai.configure(api_key=api_key_loaded)

# --- Initialize the Google Generative AI Model ---
try:
    # Using 'models/gemini-1.5-flash-latest' as it's efficient for text generation.
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Fehler beim Initialisieren des Gemini-Modells: {e}")
    st.info("Bitte überprüfen Sie den Modellnamen und die Verfügbarkeit in Ihrem Google Cloud Projekt.")
    st.stop()

st.title("KI-Assistent für Bedienungsanleitungen 🤖")
st.write("Erstelle schnell und einfach Entwürfe für Abschnitte in Bedienungsanleitungen.")

# --- User Inputs ---
product_name = st.text_input("Produktname", placeholder="z.B. SmartHome Hub X")
# Changed to text_area for multiple topics
section_topics_input = st.text_area(
    "Themen der Abschnitte (jeder Abschnitt in einer neuen Zeile)",
    placeholder="z.B.\nInstallation und erste Inbetriebnahme\nBedienung des Geräts\nFehlerbehebung\nWartung"
)
additional_details = st.text_area("Zusätzliche Details oder Spezifikationen (optional, gilt für alle Abschnitte)",
                                 placeholder="z.B. Schritte zur WLAN-Verbindung, Sicherheitshinweise, technische Daten, Fokus auf Benutzerfreundlichkeit.")

# --- Generation Logic ---
if st.button("Gesamtes Handbuch generieren"):
    if not product_name or not section_topics_input:
        st.warning("Bitte gib den Produktnamen und mindestens ein Thema für einen Abschnitt ein, um fortzufahren.")
    else:
        # Split topics by new line and filter out empty lines
        section_topics = [topic.strip() for topic in section_topics_input.split('\n') if topic.strip()]

        if not section_topics:
            st.warning("Bitte gib mindestens ein gültiges Thema für einen Abschnitt ein.")
            st.stop()

        generated_sections = []
        full_manual_text = []

        # Define the system instruction (consistent for all sections)
        system_instruction = "Du bist ein erfahrener technischer Redakteur und hilfst dabei, klare und prägnante Bedienungsanleitungen zu erstellen."

        # Loop through each section topic
        for i, topic in enumerate(section_topics):
            st.info(f"Generiere Abschnitt {i+1}/{len(section_topics)}: '{topic}'...")

            # Construct the user prompt for the current section
            prompt_text = f"""
            {system_instruction}

            Erstelle einen detaillierten Abschnitt für eine Bedienungsanleitung.

            Produkt: {product_name}
            Thema des Abschnitts: {topic}
            """
            if additional_details:
                prompt_text += f"\nZusätzliche Details/Spezifikationen (für diesen Abschnitt relevant): {additional_details}"

            prompt_text += """
            Der Abschnitt sollte klar, prägnant, benutzerfreundlich und informativ sein.
            Verwende eine professionelle, leicht verständliche Sprache.
            Strukturiere den Text mit Überschriften (z.B. mit Markdown ### oder ##), Listen und Absätzen.
            Integriere wichtige Sicherheitshinweise oder Tipps, falls relevant für dieses Thema.
            """

            try:
                with st.spinner(f"Generiere '{topic}'..."):
                    response = model.generate_content(
                        [{"role": "user", "parts": [prompt_text]}],
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=1000, # Increased max_output_tokens for potentially longer sections
                            temperature=0.7
                        )
                    )

                section_content = ""
                if hasattr(response, 'text') and response.text:
                    section_content = response.text
                elif response and hasattr(response, 'candidates') and response.candidates:
                    section_content = response.candidates[0].text if hasattr(response.candidates[0], 'text') else "Kein Text generiert für diesen Abschnitt."
                else:
                    section_content = "Kein Text generiert für diesen Abschnitt. Möglicherweise ein API-Problem oder Inhaltsfilter."

                generated_sections.append({"topic": topic, "content": section_content})
                full_manual_text.append(f"# {topic}\n\n{section_content}\n\n---") # Add to full manual with a separator

            except Exception as e:
                st.error(f"Ein Fehler ist beim Generieren von Abschnitt '{topic}' aufgetreten: {e}")
                st.info("Bitte stelle sicher, dass dein Google API-Schlüssel korrekt ist, die Gemini API aktiviert ist und du ausreichend Guthaben hast. Auch Modellverfügbarkeit prüfen.")
                generated_sections.append({"topic": topic, "content": f"Fehler: {e}"}) # Add error to section
                full_manual_text.append(f"# {topic}\n\nFEHLER BEIM GENERIEREN: {e}\n\n---") # Add error to full manual

        st.subheader("Generierte Abschnitte (Gesamtes Handbuch):")

        # Display all sections
        for section in generated_sections:
            st.markdown(f"**Thema:** {section['topic']}")
            st.markdown(section['content'])
            st.markdown("---") # Visual separator between sections in display

        # Prepare full manual for download
        final_manual_output = "\n\n".join(full_manual_text)

        st.code(final_manual_output, language='markdown') # Show the raw text for easy copying

        st.download_button(
            label="Gesamtes Handbuch herunterladen",
            data=final_manual_output.encode('utf-8'), # Encode for download
            file_name=f"Bedienungsanleitung_{product_name.replace(' ', '_')}_Komplett.md", # .md for markdown
            mime="text/markdown"
        )
