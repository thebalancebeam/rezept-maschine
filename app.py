import streamlit as st
import json
from openai import OpenAI

# ----------------------------------
# CONFIG
# ----------------------------------
st.set_page_config(page_title="🍳 KI-Rezeptmaschine", layout="wide")

st.title("🍳 KI-Rezeptmaschine")
st.markdown("Gib deine Zutaten ein und erhalte passende Rezepte – erzeugt durch KI.")

# OpenAI Client (API-Key muss in Streamlit Secrets gesetzt werden)
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

# ----------------------------------
# UI – Zutaten-Eingabe
# ----------------------------------
st.sidebar.header("Zutaten eingeben")
zutaten = st.sidebar.text_area(
    "Welche Zutaten hast du gerade zu Hause?",
    placeholder="z. B. Nudeln, Tomaten, Paprika, Käse"
)

# Button
start = st.sidebar.button("🔍 Rezepte suchen")

# Prompt Template
PROMPT_TEMPLATE = """
Du bist ein professioneller Koch und KI-Rezeptersteller. 
Erstelle Rezeptvorschläge basierend auf den vom Nutzer eingegebenen Zutaten.

WICHTIG:
- Gewürze, Salz, Pfeffer, Öl, Wasser und gängige Küchenbasics dürfen immer genutzt werden und zählen nicht als Zutaten.
- Gib die Ausgabe AUSSCHLIESSLICH als gültiges JSON-Objekt zurück.
- Keine Erklärungen, kein Fließtext, keine Kommentare.

--------------------------------------------------
AUFGABEN
--------------------------------------------------

1) STRIKTE REZEPTE (strict_recipes)
Erstelle GENAU 4 Rezepte, die AUSSCHLIESSLICH die vom Nutzer angegebenen Zutaten verwenden.
Keine weiteren Zutaten hinzufügen, außer Gewürzen oder Öl.
Format jedes Rezeptes:

{{
  "title": "",
  "description": "",
  "ingredients": ["", ""],
  "steps": ["", ""]
}}

2) ERWEITERTE REZEPTE (extended_recipes)
Erstelle GENAU 3 zusätzliche Rezepte, bei denen du MINIMAL notwendige Zutaten ergänzen darfst.
Format identisch wie oben.

--------------------------------------------------
EINGABEDATEN
--------------------------------------------------
User-Zutaten: {USER_INGREDIENTS}

--------------------------------------------------
AUSGABESTRUKTUR (verpflichtend)
--------------------------------------------------
{{
  "strict_recipes": [...],
  "extended_recipes": [...]
}}
"""

# ----------------------------------
# KI Anfrage
# ----------------------------------
if start:
    if not zutaten.strip():
        st.error("Bitte gib zuerst Zutaten ein.")
        st.stop()

    with st.spinner("Rezepte werden generiert…"):
        prompt = PROMPT_TEMPLATE.replace("{USER_INGREDIENTS}", zutaten)

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message["content"]

        try:
            rezepte = json.loads(raw)
        except:
            st.error("Fehler: Die KI hat kein gültiges JSON zurückgegeben.")
            st.code(raw)
            st.stop()

        # Ausgabe-Bereich
        st.header("Ergebnisse")

        # ------ Strikte Rezepte ------
        st.subheader("🔒 Strikte Rezepte (nur deine Zutaten)")
        for r in rezepte.get("strict_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("### Zutaten")
                st.write("\n".join([f"• {x}" for x in r.get("ingredients", [])]))
                st.markdown("### Schritte")
                st.write("\n".join([f"{i+1}. {step}" for i, step in enumerate(r.get("steps", []))]))

        # ------ Erweiterte Rezepte ------
        st.subheader("✨ Erweiterte Rezepte (mit minimalen Ergänzungen)")
        for r in rezepte.get("extended_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("### Zutaten")
                st.write("\n".join([f"• {x}" for x in r.get("ingredients", [])]))
                st.markdown("### Schritte")
                st.write("\n".join([f"{i+1}. {step}" for i, step in enumerate(r.get("steps", []))]))
