import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="CFO Edubot - Evaluación Dinámica",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ACCESO SEGURO A LA API KEY DESDE LOS SECRETS DE STREAMLIT
try:
    # Busca la clave guardada en la "caja fuerte" de Streamlit
    api_key_segura = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key_segura)
except Exception as e:
    st.error("Error de configuración: No se encontró la API Key en los secretos del servidor.")

# Nombre del estudiante para el reporte
nombre_estudiante = st.sidebar.text_input("Nombre del Estudiante:", value="Estudiante de Analisis Financiero - Minería")

# SYSTEM INSTRUCTIONS DEL TUTOR
SYSTEM_INSTRUCTIONS = """
Asume el rol de un Director de Finanzas (CFO) Corporativo de una gran compañía minera y Tutor Académico. Tu objetivo es guiar al estudiante de manera interactiva y socrática en la asignatura de "Análisis de Estados Financieros para la Toma de Decisiones en el Sector Minero Peruano bajo Volatilidad Global".
A lo largo del chat evaluarás su criterio financiero. 
"""

# Inicialización de estados
if "chat" not in st.session_state and "api_key" in st.session_state:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTIONS
        )
        st.session_state.chat = model.start_chat(history=[])
        response = st.session_state.chat.send_message("Inicia la FASE 1 saludando al estudiante de manera ejecutiva.")
        st.session_state.messages = [{"role": "assistant", "content": response.text}]
        st.session_state.preguntas_examen = None
    except Exception as e:
        st.error(f"Error al inicializar el modelo: {e}")

# DISTRIBUCIÓN DE PANTALLA: PANELES Y PESTAÑAS
col_datos, col_interactiva = st.columns([0.4, 0.6])

with col_datos:
    st.title("📊 Estados Financieros")
    with st.expander("💼 Caso: Compañía Minera Los Andes SAC", expanded=True):
        st.write("**Entorno:** Volatilidad de metales, 25 días de paro vial, y shock de precios de diésel por conflictos geopolíticos.")
    with st.expander("📉 Balance General Corto (Miles USD)"):
        st.write("Año 1: Act. Corriente: $180,000 (Efec: $45K, Inv: $65K) | Pas. Corriente: $95,000")
        st.write("Año 2: Act. Corriente: $210,000 (Efec: $15K, Inv inmovilizado: $105K) | Pas. Corriente: $165,000")
    with st.expander("📈 Estado de Resultados (Miles USD)"):
        st.write("Año 1: Ventas: $520,000 | Costo de Ventas: $310,000 | Utilidad Neta: $85,000")
        st.write("Año 2: Ventas: $550,000 | Costo de Ventas: $445,000 | Utilidad Neta: $24,500")

with col_interactiva:
    # Separamos en dos pestañas la interacción
    tab1, tab2 = st.tabs(["💬 Chat Socrático", "📝 Examen Personalizado"])
    
    with tab1:
        st.subheader("Discusión de Casos con el CFO")
        if "api_key" in st.session_state:
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            
            if user_input := st.chat_input("Escribe tu análisis al CFO..."):
                with chat_container:
                    st.chat_message("user").write(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                with st.spinner("El CFO evalúa tu respuesta..."):
                    res = st.session_state.chat.send_message(user_input)
                with chat_container:
                    st.chat_message("assistant").write(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})

    with tab2:
        st.subheader("Evaluación Escrita a Medida")
        st.write("El CFO generará preguntas de opción múltiple únicas basándose en tu desempeño en el chat.")
        
        # Botón para detonar la creación de preguntas exclusivas vía JSON
        if st.button("Generar mi Examen Único"):
            prompt_evaluacion = """
            Genera 3 preguntas de opción múltiple únicas para este estudiante. Adáptalas a lo que hemos conversado en el chat.
            Debes responder UNICAMENTE con un objeto JSON estructurado exactamente así, sin markdown extra, sin la palabra ```json:
            {
              "preguntas": [
                {
                  "id": 1,
                  "pregunta": "Escribe aquí la pregunta basada en el balance o entorno minero...",
                  "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                  "correcta": "La opción exacta escrita de la misma forma"
                }
              ]
            }
            """
            try:
                with st.spinner("El CFO está redactando tus preguntas..."):
                    response_json = st.session_state.chat.send_message(prompt_evaluacion).text
                    # Limpieza por si el modelo incluye marcas de código
                    response_json = response_json.replace("```json", "").replace("```", "").strip()
                    st.session_state.preguntas_examen = json.loads(response_json)["preguntas"]
                    st.success("¡Examen generado exitosamente! Responde abajo.")
            except Exception as e:
                st.error("Error al estructurar la evaluación. Inténtalo de nuevo.")
        
        # Si las preguntas ya fueron cargadas en la sesión, las pintamos como un formulario
        if st.session_state.get("preguntas_examen"):
            respuestas_usuario = {}
            with st.form("formulario_evaluacion"):
                for idx, item in enumerate(st.session_state.preguntas_examen):
                    st.markdown(f"**Pregunta {idx+1}:** {item['pregunta']}")
                    respuestas_usuario[item['id']] = st.radio(
                        "Selecciona tu respuesta:",
                        options=item['opciones'],
                        key=f"p_{item['id']}"
                    )
                    st.write("---")
                
                enviar_evaluacion = st.form_submit_button("Enviar Respuestas al Docente")
                
                if enviar_evaluacion:
                    # Calificación automatizada
                    respuestas_correctas = 0
                    total_preguntas = len(st.session_state.preguntas_examen)
                    reporte_respuestas = []
                    
                    for item in st.session_state.preguntas_examen:
                        resp_estudiante = respuestas_usuario[item['id']]
                        es_correcta = resp_estudiante == item['correcta']
                        if es_correcta:
                            respuestas_correctas += 1
                        
                        reporte_respuestas.append({
                            "Pregunta": item['pregunta'],
                            "Respuesta_Estudiante": resp_estudiante,
                            "Respuesta_Correcta": item['correcta'],
                            "Resultado": "Correcto" if es_correcta else "Incorrecto"
                        })
                    
                    nota_final = (respuestas_correctas / total_preguntas) * 20 # Escala vigesimal típica de Perú
                    st.metric(label="Calificación de la Evaluación", value=f"{nota_final:.1f} / 20.0")
                    
                    # Crear el archivo descargable de soporte para el docente
                    df_reporte = pd.DataFrame(reporte_respuestas)
                    df_reporte["Estudiante"] = nombre_estudiante
                    df_reporte["Nota"] = nota_final
                    
                    csv = df_reporte.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📥 Descargar Hoja de Respuestas para el Profesor (CSV)",
                        data=csv,
                        file_name=f"Evaluacion_{nombre_estudiante.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )