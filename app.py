import streamlit as st
import json
import re
import google.generativeai as genai


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

st.set_page_config(page_title="🍳 KI Rezeptmaschine", layout="wide")
st.title("🍳 KI Rezeptmaschine – Gemini")


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("Kein GEMINI_API_KEY gesetzt!")
    st.stop()

genai.configure(api_key=api_key)


# ---------------------------------------------------------
# MODELL
# ---------------------------------------------------------
# HIER dein funktionierendes Modell einsetzen
model_name = "models/gemini-2.5-flash-lite"


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

zutaten = st.text_area("Welche Zutaten hast du?")
start = st.button("🔍 Rezepte suchen")


# ---------------------------------------------------------
# PROMPT
# ---------------------------------------------------------

prompt_template = """
Du bist ein professioneller Koch und erstellt Rezepte.

Du erhältst vom Nutzer eine Zutatenliste.

Regeln:
- Gewürze, Salz, Pfeffer, Öl zählen NICHT als Zutaten.
- Benutze für strict_recipes ausschließlich die vom Nutzer genannten Zutaten.
- Du musst exakt erstellen:
    1) strict_recipes → GENAU 4 Rezepte
    2) extended_recipes → GENAU 3 Rezepte mit minimalen realistischen Ergänzungen
- Keine Erklärungen.
- Keine Vorbemerkungen.
- Keine Nachbemerkungen.
- Du darfst NUR reines JSON liefern.
- JSON muss komplett gültig sein.
- Kein Markdown.
- Kein ``` Codeblock.
- Wenn du Fehler machst, musst du den JSON korrigieren.

Format jedes Rezepts:

{
  "title": "",
  "description": "",
  "ingredients": [],
  "steps": []
}

Zutaten des Users:
{ING}
"""


# ---------------------------------------------------------
# JSON SAFE PARSER
# ---------------------------------------------------------

def safe_json_load(text):
    """extrahiert robust JSON aus KI-Ausgaben"""

    # codeblocks entfernen
    text = re.sub(r"```(json)?", "", text)

    # nur JSON extrahieren
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Kein JSON gefunden.")

    cleaned = text[start:end+1]
    return json.loads(cleaned)


# ---------------------------------------------------------
# GENERATE
# ---------------------------------------------------------

if start:

    if not zutaten.strip():
        st.error("Bitte zuerst Zutaten eingeben.")
        st.stop()

    prompt = prompt_template.replace("{ING}", zutaten)

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        raw = response.text
    except Exception as e:
        st.error("Gemini Fehler: " + str(e))
        st.stop()

    try:
        data = safe_json_load(raw)
    except Exception as e:
        st.error("Ungültiges JSON: " + str(e))
        st.code(raw)
        st.stop()


    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    st.header("Ergebnisse")

    for section in ["strict_recipes", "extended_recipes"]:

        st.subheader(section.replace("_", " ").title())

        for rec in data.get(section, []):

            with st.expander(rec.get("title", "Rezept")):

                st.write(rec.get("description", ""))

                st.markdown("**Zutaten**")
                st.write(rec.get("ingredients", []))

                st.markdown("**Schritte**")
                for i, s in enumerate(rec.get("steps", []), 1):
                    st.write(f"{i}. {s}")
