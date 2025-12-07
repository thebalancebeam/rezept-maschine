import streamlit as st
import google.generativeai as genai

st.title("🔍 Verfügbare Gemini Modelle")

api_key = st.text_input("Gib deinen GEMINI API Key ein:", type="password")

if not api_key:
    st.info("Bitte API Key eingeben.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    models = genai.list_models()
except Exception as e:
    st.error(f"Fehler beim Abrufen: {e}")
    st.stop()

st.subheader("Modelle, die Textgenerierung unterstützen:")

good = []

for m in models:
    if "generateContent" in m.supported_generation_methods:
        good.append(m.name)

if not good:
    st.warning("Kein Modell gefunden.")
else:
    for name in good:
        st.write("✅", name)
