import streamlit as st
import json
import google.generativeai as genai


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

st.set_page_config(page_title="🍳 KI Rezeptmaschine", layout="wide")
st.title("🍳 KI Rezeptmaschine – Gemini Edition")


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("Kein GEMINI_API_KEY gesetzt!")
    st.stop()

genai.configure(api_key=api_key)


# ---------------------------------------------------------
# Wähle dein Modell
# ---------------------------------------------------------
# !!! HIER DEN MODELLNAMEN EINSETZEN !!!
# Beispiel:
# model_name = "models/gemini-1.5-pro-latest"
# oder
# model_name = "models/gemini-2.0-flash"
#
# Wenn du ihn noch nicht kennst → sag Bescheid,
# dann schreibe ich dir die Model-Lister App.

model_name = "models/gemini-1.5-pro-latest"



# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

zutaten = st.text_area("Welche Zutaten hast du?")

start = st.button("🔍 Rezepte suchen")


# ---------------------------------------------------------
# PROMPT
# ---------------------------------------------------------

prompt_template = """
Du bist ein professioneller Koch.

Erstelle basierend auf den Zutaten Rezepte.

Regeln:
- Gewürze zählen nicht als Zutaten.
- Gib die Antwort ausschließlich im JSON Format.
- Kein Text außerhalb von JSON.

Erstelle:
1) strict_recipes → genau 4 Rezepte nur mit den vorhandenen Zutaten.
2) extended_recipes → genau 3 Rezepte mit minimalen realistischen Ergänzungen.

Format pro Rezept:

{
 "title": "...",
 "description": "...",
 "ingredients": [],
 "steps": []
}

Zutaten des Users:
{ING}
"""


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


    # --------------------------------------------------------
    # JSON PARSEN
    # --------------------------------------------------------

    try:
        data = json.loads(raw)
    except Exception:
        st.error("Die KI hat kein gültiges JSON geliefert.")
        st.code(raw)
        st.stop()


    # --------------------------------------------------------
    # AUSGABE
    # --------------------------------------------------------

    st.header("Ergebnisse")

    for section in ["strict_recipes", "extended_recipes"]:

        st.subheader(section.replace("_"," ").title())

        for rec in data.get(section, []):

            with st.expander(rec.get("title","Rezept")):

                st.write(rec.get("description",""))

                st.markdown("**Zutaten**")
                st.write(rec.get("ingredients",[]))

                st.markdown("**Schritte**")
                for i,s in enumerate(rec.get("steps",[]),1):
                    st.write(f"{i}. {s}")
