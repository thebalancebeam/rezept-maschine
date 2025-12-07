import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(page_title="🍳 KI-Rezeptmaschine", layout="wide")

st.title("🍳 KI-Rezeptmaschine")
st.markdown("Gib deine Zutaten ein und erhalte passende Rezepte – erzeugt durch KI.")

# API Key
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Kein GEMINI_API_KEY gesetzt.")
    st.stop()

genai.configure(api_key=api_key)

# UI
st.sidebar.header("Zutaten eingeben")
zutaten = st.sidebar.text_area("Welche Zutaten hast du?", "")
start = st.sidebar.button("🔍 Rezepte suchen")

# Prompt
PROMPT = """
Du bist ein professioneller Koch ...
(Gleicher Prompt wie vorher)
User-Zutaten: {ING}
"""

if start:
    if not zutaten.strip():
        st.error("Bitte Zutaten eingeben.")
        st.stop()

    prompt = PROMPT.replace("{ING}", zutaten)

    with st.spinner("Rezepte werden generiert…"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
            response = model.generate_content(prompt)
            raw = response.text
        except Exception as e:
            st.error(f"Gemini Fehler: {e}")
            st.stop()

        try:
            data = json.loads(raw)
        except Exception:
            st.error("Kein gültiges JSON erhalten")
            st.code(raw)
            st.stop()

        st.header("Ergebnisse")

        st.subheader("🔒 Strikte Rezepte")
        for r in data.get("strict_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("**Zutaten**")
                st.write("\n".join(r.get("ingredients", [])))
                st.markdown("**Schritte**")
                for i, step in enumerate(r.get("steps", []), 1):
                    st.write(f"{i}. {step}")

        st.subheader("✨ Erweiterte Rezepte")
        for r in data.get("extended_recipes", []):
            with st.expander(r.get("title", "Rezept")):
                st.write(r.get("description", ""))
                st.markdown("**Zutaten**")
                st.write("\n".join(r.get("ingredients", [])))
                st.markdown("**Schritte**")
                for i, step in enumerate(r.get("steps", []), 1):
                    st.write(f"{i}. {step}")
