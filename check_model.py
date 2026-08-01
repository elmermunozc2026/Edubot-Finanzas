"""
CFO Agent IA - Script de Diagnóstico del Modelo
Ejecutar UNA SOLA VEZ para identificar el modelo disponible en tu cuenta.

USO:
    streamlit run check_model.py
    -- o --
    python check_model.py  (si tienes la API key en variable de entorno)
"""
import os

# ── INTENTO 1: Streamlit (producción) ────────────────────────────────────────
try:
    import streamlit as st

    st.set_page_config(page_title="CFO Agent IA — Diagnóstico de Modelo", page_icon="🔍", layout="centered")
    st.title("🔍 Diagnóstico de Modelo Gemini")
    st.caption("Identifica el nombre exacto del modelo disponible en tu cuenta de Google AI Studio.")
    st.divider()

    # Obtener API Key
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("✅ API Key encontrada en Streamlit Secrets")
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            st.success("✅ API Key encontrada en variable de entorno")
        else:
            api_key = st.text_input(
                "🔑 Ingresa tu API Key de Google AI Studio:",
                type="password",
                placeholder="AIza...",
            )

    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        st.subheader("📋 Modelos disponibles en tu cuenta")

        try:
            modelos = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    modelos.append({
                        "Nombre del Modelo (usar en código)": m.name,
                        "Nombre para mostrar": getattr(m, "display_name", m.name),
                        "Versión": getattr(m, "version", "N/D"),
                    })

            if modelos:
                import pandas as pd
                df = pd.DataFrame(modelos)
                st.dataframe(df, use_container_width=True)

                st.divider()
                st.subheader("🎯 ¿Cuál usar en orchestrator.py?")

                # Detectar el mejor modelo disponible
                nombres = [m["Nombre del Modelo (usar en código)"] for m in modelos]
                recomendado = None
                prioridad = [
                    "gemini-2.5-flash", "gemini-2.0-flash",
                    "gemini-1.5-flash", "gemini-1.5-pro",
                    "gemini-pro",
                ]
                for p in prioridad:
                    for n in nombres:
                        if p in n:
                            recomendado = n
                            break
                    if recomendado:
                        break

                if recomendado:
                    st.success(f"✅ Modelo recomendado detectado: **{recomendado}**")
                    st.code(f'model_name="{recomendado}"', language="python")
                    st.info(
                        "📋 Copia este nombre y reemplázalo en **agent/orchestrator.py** "
                        "en el parámetro `model_name` del `CFOOrchestrator.__init__()`"
                    )
                else:
                    st.warning("⚠️ No se detectó automáticamente un modelo recomendado. Elige uno de la tabla de arriba.")

                st.divider()
                st.subheader("🧪 Prueba rápida del modelo")
                modelo_sel = st.selectbox(
                    "Selecciona el modelo a probar:",
                    nombres,
                    index=nombres.index(recomendado) if recomendado in nombres else 0,
                )
                if st.button("🚀 Probar modelo seleccionado", type="primary"):
                    with st.spinner(f"Probando {modelo_sel}..."):
                        try:
                            model = genai.GenerativeModel(model_name=modelo_sel)
                            resp = model.generate_content(
                                "Responde en una sola línea: ¿Cuál es el ratio de liquidez corriente si el activo corriente es 500 y el pasivo corriente es 250?"
                            )
                            st.success(f"✅ Modelo funciona correctamente")
                            st.markdown(f"**Respuesta de prueba:** {resp.text}")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error al probar el modelo: {e}")

                st.divider()
                st.subheader("📝 Código listo para copiar")
                st.markdown("Reemplaza el `__init__` de `CFOOrchestrator` en `agent/orchestrator.py`:")
                st.code(f'''
class CFOOrchestrator:
    def __init__(
        self,
        api_key: str,
        mode: str = "tutor",
        sector: str = "mining",
        model_name: str = "{recomendado or 'TU_MODELO_AQUI'}",  # ← Modelo identificado
        lang: str = "es",
    ):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=get_system_prompt(mode, sector, lang),
            tools=TOOL_DECLARATIONS,
        )
''', language="python")

            else:
                st.warning("⚠️ No se encontraron modelos con soporte generateContent en tu cuenta.")

        except Exception as e:
            st.error(f"❌ Error al listar modelos: {e}")
            st.info("Verifica que tu API Key sea válida y tenga permisos en Google AI Studio.")
    else:
        st.info("👆 Ingresa tu API Key para comenzar el diagnóstico.")

    st.divider()
    st.caption("CFO Agent IA © 2026 | Script de diagnóstico — No incluir en producción")

# ── INTENTO 2: Script Python puro (sin Streamlit) ────────────────────────────
except ImportError:
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = input("Ingresa tu API Key de Google AI Studio: ").strip()

    genai.configure(api_key=api_key)

    print("\n" + "="*60)
    print("CFO Agent IA — Diagnóstico de Modelos Disponibles")
    print("="*60)

    modelos_disponibles = []
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            modelos_disponibles.append(m.name)
            print(f"  ✅ {m.name}")

    print("\n" + "="*60)
    print("RECOMENDACIÓN para orchestrator.py:")
    prioridad = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
    for p in prioridad:
        for n in modelos_disponibles:
            if p in n:
                print(f'  model_name="{n}"')
                break
    print("="*60 + "\n")