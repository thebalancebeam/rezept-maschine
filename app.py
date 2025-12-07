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
    st.error("Kein OPENAI_API_KEY gesetzt.")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------------------
# UI
# ------------------------------
st.sidebar.header("Zutaten eingeben")
zutaten = st.sidebar.text_area("Welche Zutaten hast du?", "")
start = st.sidebar.button("🔍 Rezepte suchen")

# ------------------------------
# PROMPT
# ------------------------------
PROMPT = '''
Du bist ein professioneller Koch.
Erstelle Rezepte basierend auf den Zutaten.
Regeln:
- Gewürze zählen nicht als Zutaten.
- Ausgabe ausschließlich JSON.
- 4 strict_recipes ohne Zusatz-Zutaten.
- 3 extended_recipes mit minimalen realistischen Zusätzen.

User-Zutaten: {ING}
'''

# ------------------------------
# GENERATE
# ------------------------------
if start:
    if not zutaten.strip():
        st.error("Bitte zuerst Zutaten eingeben.")
        st.stop()

    prompt = PROMPT.replace('{ING}', zutaten)

    with st.spinner("Rezepte werden generiert…"):
        try:
            r = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user", "content": prompt}]
            )
            raw = r.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI Fehler: {e}")
            st.stop()

        try:
            data = json.loads(raw)
        except Exception:
            st.error("Ungültiges JSON von der KI")
            st.code(raw)
            st.stop()

        st.header("Ergebnisse")

        st.subheader("🔒 Strikte Rezepte")
        for rec in data.get('strict_recipes', []):
            with st.expander(rec.get('title','Rezept')):
                st.write(rec.get('description',''))
                st.markdown('**Zutaten**')
                st.write('
'.join(rec.get('ingredients',[])))
                st.markdown('**Schritte**')
                for i,s in enumerate(rec.get('steps',[]),1):
                    st.write(f"{i}. {s}")

        st.subheader("✨ Erweiterte Rezepte")
        for rec in data.get('extended_recipes', []):
            with st.expander(rec.get('title','Rezept')):
                st.write(rec.get('description',''))
                st.markdown('**Zutaten**')
                st.write('
'.join(rec.get('ingredients',[])))
                st.markdown('**Schritte**')
                for i,s in enumerate(rec.get('steps',[]),1):
                    st.write(f"{i}. {s}")
