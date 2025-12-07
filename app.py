import streamlit as st
import json
from openai import OpenAI

# API Key
api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.error("Kein OPENAI_API_KEY gesetzt.")
    st.stop()

client = OpenAI(api_key=api_key)
()

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
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI Fehler: {e}")
            st.stop()
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
