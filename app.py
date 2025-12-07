import streamlit as st
import json
from openai import OpenAI

# ------------------------------
# PAGE
# ------------------------------
st.set_page_config(page_title="🍳 KI-Rezeptmaschine", layout="wide")

st.title("🍳 KI-Rezeptmaschine")
st.write("Gib deine Zutaten ein und erhalte passende Rezepte.")

# ------------------------------
# OPENAI
# ------------------------------
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.error("Kein OPENAI_API_KEY gesetzt!")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# UI
# ------------------------------
st.sidebar.header("Zutaten eingeben")
zutaten = st.sidebar.text_area(
    "Welche Zutaten hast du?",
    ""
)

start = st.sidebar.button("🔍 Rezepte suchen")

# ------------------------------
# PROMPT
# ------------------------------
PROMPT = """
Du bist ein professioneller Koch.

Erstelle Rezeptvorschläge basierend auf den vom Nutzer eingegebenen Zutaten.

Regeln:
- Gewürze, Salz, Pfeffer, Öl zählen nicht als Zutaten.
- Gib die Ausgabe ausschließlich als JSON aus.
- Keine Erklärungen.

Erstelle:
1) strict_recipes → genau 4 Rezepte nur mit den Zutaten des Users.
2) extended_recipes → genau 3 Rezepte mit minimalen Zusatz-Zutaten.

Format jedes Rezepts:
{
 "title": "",
 "description": "",
 "ingredients": [],
 "steps": []
}

User-Zutaten:
{ING}
"""

# ------------------------------
# GENERATE
# ------------------------------
if start:

    if not zutaten.strip():
        st.error("Bitte zuerst Zutaten eingeben.")
        st.stop()

    prompt = PROMPT.replace("{ING}", zutaten)

    with st.spinner("Rezepte werden generiert…"):

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI Fehler: {e}")
            st.stop()

        # JSON prüfen
        try:
            data = json.loads(raw)
        except Exception:
            st.error("Die KI hat kein gültiges JSON geliefert.")
            st.code(raw)
            st.stop()

        # --------------------------
        # OUTPUT
        # --------------------------
        st.header("Ergebnisse")

        st.subheader("🔒 Strikte Rezepte")
        for r in data.get("strict_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("**Zutaten**")
                st.write("\n".join(r.get("ingredients", [])))
                st.markdown("**Schritte**")
                for i, s in enumerate(r.get("steps", []), 1):
                    st.write(f"{i}. {s}")

        st.subheader("✨ Erweiterte Rezepte")
        for r in data.get("extended_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("**Zutaten**")
                st.write("\n".join(r.get("ingredients", [])))
                st.markdown("**Schritte**")
                for i, s in enumerate(r.get("steps", []), 1):
                    st.write(f"{i}. {s}")
