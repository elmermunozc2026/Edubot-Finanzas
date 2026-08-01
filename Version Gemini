# check_model.py — Ejecutar UNA SOLA VEZ para identificar el modelo
import google.generativeai as genai
import streamlit as st

# Usa el mismo método que tu app.py actual
api_key = st.secrets["GEMINI_API_KEY"]  
genai.configure(api_key=api_key)

print("✅ Modelos disponibles en tu cuenta:\n")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  → {m.name}")
