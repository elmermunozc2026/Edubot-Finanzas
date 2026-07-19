import streamlit as st
import google.generativeai as genai
# Forzamos la versión v1 de la API antes de configurar la clave
genai.api_v1_level = True 

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

import pandas as pd
import json
import random

# ==========================================
#      CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CFO Edubot - Evaluación Dinámica", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ACCESO SEGURO A LA API KEY DESDE LOS SECRETS DE STREAMLIT
try:
    api_key_segura = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key_segura)
except Exception as e:
    st.error("Error de configuración: No se encontró la API Key en los secretos del servidor.")

# ==========================================
#      CONTROL DE ACCESO (LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso Autorizado - Edubot Finanzas")
    st.write("Por favor, introduce tus credenciales de estudiante para ingresar a la plataforma de evaluación.")
    
    with st.form("formulario_login"):
        correo_input = st.text_input("Correo electrónico institucional:").strip().lower()
        password_input = st.text_input("Contraseña temporal del curso:", type="password")
        boton_ingresar = st.form_submit_button("Ingresar al Edubot")
        
        if boton_ingresar:
            password_valida = st.secrets["accesos_alumnos"]["password_temporal"]
            correos_validos = [c.lower() for c in st.secrets["accesos_alumnos"]["correos_autorizados"]]
            
            if correo_input in correos_validos and password_input == password_valida:
                st.session_state.autenticado = True
                st.session_state.correo_usuario = correo_input
                nombre_defecto = correo_input.split("@")[0].replace(".", " ").title()
                st.session_state.nombre_estudiante = nombre_defecto
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("El correo no está registrado como autorizado o la contraseña es incorrecta.")
    st.stop()

# ==========================================
#      BANCO DE CASOS MINEROS
# ==========================================
CASOS_MINEROS = [
    {
        "titulo": "Caso A: Paros Viales e Inmovilización",
        "entorno": "Volatilidad de metales, 25 días de paro vial, y shock de precios de diésel por conflictos geopolíticos.",
        "balance_a1": "Act. Corriente: $180,000 (Efec: $45K, Inv: $65K) | Pas. Corriente: $95,000",
        "balance_a2": "Act. Corriente: $210,000 (Efec: $15K, Inv inmovilizado: $105K) | Pas. Corriente: $165,000",
        "resultados_a1": "Ventas: $520,000 | Costo de Ventas: $310,000 | Utilidad Neta: $85,000",
        "resultados_a2": "Ventas: $550,000 | Costo de Ventas: $445,000 | Utilidad Neta: $24,500",
        "mensaje_inicial": "Veo que nuestro inventario se disparó a $105K y la caja cayó a $15K en el Año 2 debido a los paros viales. ¿Qué medidas de capital de trabajo me propones para mitigar este shock de liquidez?"
    },
    {
        "titulo": "Caso B: Caída de Precios del Cobre y Sobreproducción",
        "entorno": "Desaceleración de la demanda asiática, caída del 18% en el precio del cobre y acumulación de concentrado en almacén.",
        "balance_a1": "Act. Corriente: $200,000 (Efec: $60K, Inv: $50K) | Pas. Corriente: $80,000",
        "balance_a2": "Act. Corriente: $195,000 (Efec: $10K, Inv inmovilizado: $120K) | Pas. Corriente: $110,000",
        "resultados_a1": "Ventas: $600,000 | Costo de Ventas: $350,000 | Utilidad Neta: $110,000",
        "resultados_a2": "Ventas: $480,000 | Costo de Ventas: $410,000 | Utilidad Neta: $12,000",
        "mensaje_inicial": "El precio del cobre se desplomó y nos quedamos con stock masivo sobrevalorado. La caja bajó a $10K y el inventario subió a $120K. ¿Cómo reestructurarías el ciclo de conversión de efectivo ante este escenario?"
    },
    {
        "titulo": "Caso C: Retraso en Permisos Ambientales y Costos de Mantenimiento",
        "entorno": "Demoras burocráticas en la expansión del tajo abierto, paralización temporal de planta y penalizaciones contractuales.",
        "balance_a1": "Act. Corriente: $150,000 (Efec: $40K, Inv: $40K) | Pas. Corriente: $70,000",
        "balance_a2": "Act. Corriente: $160,000 (Efec: $8K, Inv acumulado: $85K) | Pas. Corriente: $130,000",
        "resultados_a1": "Ventas: $450,000 | Costo de Ventas: $280,000 | Utilidad Neta: $65,000",
        "resultados_a2": "Ventas: $390,000 | Costo de Ventas: $360,000 | Utilidad Neta: -$5,000",
        "mensaje_inicial": "La paralización operativa nos está costando caro: registramos pérdida neta y la caja está en niveles críticos de $8K. ¿Qué financiamiento de corto plazo o estrategia con proveedores sugieres?"
    }
]

# INSTRUCCIONES DEL SISTEMA PARA EL MODELO
SYSTEM_INSTRUCTIONS = """
Asume el rol de un Director de Finanzas (CFO) Corporativo de una gran compañía minera y Tutor Académico. Tu objetivo es guiar al estudiante de manera interactiva y socrática en la asignatura de "Análisis de Estados Financieros para la Toma de Decisiones en el Sector Minero Peruano bajo Volatilidad Global". A lo largo del chat evaluarás su criterio financiero.
"""

# ==========================================
#     CÓDIGO PRINCIPAL Y CONTROL DE SESIÓN
# ==========================================
nombre_estudiante = st.sidebar.text_input("Nombre del Estudiante:", value=st.session_state.nombre_estudiante)

# CONTROL DEL BOTÓN DE REINICIO (SÓLO AQUÍ EN LA BARRA LATERAL)
with st.sidebar:
    st.write("---")
    if st.button("🔄 Cambiar de Caso (Reiniciar)", use_container_width=True):
        st.session_state.pop("caso_seleccionado", None)
        st.session_state.pop("chat", None)
        st.session_state.pop("messages", None)
        st.session_state.pop("preguntas_examen", None)
        st.rerun()

# SELECCIÓN ÚNICA Y PERSISTENTE DEL CASO ALEATORIO
if "caso_seleccionado" not in st.session_state:
    st.session_state.caso_seleccionado = random.choice(CASOS_MINEROS)

# INICIALIZACIÓN DEL MODELO DE GEMINI Y MENSAJE INICIAL
if "messages" not in st.session_state:
    try:
       # Inicializamos el modelo de forma directa y limpia
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_INSTRUCTIONS
        )
        st.session_state.chat = model.start_chat(history=[])
        
        caso = st.session_state.caso_seleccionado
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hola {nombre_estudiante}. Soy el CFO de la minera. {caso['mensaje_inicial']}"}
        ]
        st.session_state.preguntas_examen = None
    except Exception as e:
        st.error(f"Error al inicializar el modelo: {e}")

# ==========================================
#    DISTRIBUCIÓN DE PANTALLA: PANELES
# ==========================================
col_datos, col_interactiva = st.columns([0.4, 0.6])

with col_datos:
    st.title("📊 Estados Financieros")
    
    caso_actual = st.session_state.caso_seleccionado
    
    with st.expander(f"💼 {caso_actual['titulo']}", expanded=True):
        st.write(f"**Entorno:** {caso_actual['entorno']}")
        
    with st.expander("📉 Balance General Corto (Miles USD)"):
        st.write(f"{caso_actual['balance_a1']}")
        st.write(f"{caso_actual['balance_a2']}")
        
    with st.expander("📈 Estado de Resultados (Miles USD)"):
        st.write(f"{caso_actual['resultados_a1']}")
        st.write(f"{caso_actual['resultados_a2']}")

with col_interactiva:
    tab1, tab2 = st.tabs(["💬 Chat Socrático", "📝 Examen Personalizado"])
    
    with tab1:
        st.subheader("Discusión de Casos con el CFO")
        
        chat_container = st.container(height=400)
        with chat_container:
            if "messages" in st.session_state:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
        
        if user_input := st.chat_input("Escribe tu análisis al CFO..."):
            with chat_container:
                st.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                with st.spinner("El CFO evalúa tu respuesta..."):
                    res = st.session_state.chat.send_message(user_input)
                with chat_container:
                    st.chat_message("assistant").write(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error al enviar mensaje a Gemini: {e}")

    with tab2:
        st.subheader("Evaluación Escrita a Medida")
        st.write("El CFO generará preguntas de opción múltiple únicas basándose en tu desempeño en el chat.")
        
        if st.button("Generar mi Examen Único"):
            prompt_evaluacion = """
            Genera 3 preguntas de opción múltiple únicas para este estudiante. Adáptalas a lo que hemos conversado en el chat. Debes responder UNICAMENTE con un objeto JSON estructurado exactamente así, sin markdown extra, sin la palabra ```json:
            {"preguntas": [{"id": 1, "pregunta": "Escribe aquí la pregunta basada en el balance o entorno minero...", "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"], "correcta": "La opción exacta escrita de la misma forma"}]}
            """
            try:
                with st.spinner("El CFO está redactando tus preguntas..."):
                    response_json = st.session_state.chat.send_message(prompt_evaluacion).text
                    response_json = response_json.replace("```json", "").replace("```", "").strip()
                    st.session_state.preguntas_examen = json.loads(response_json)["preguntas"]
                st.success("¡Examen generado exitosamente! Responde abajo.")
            except Exception as e:
                st.error(f"Error al estructurar la evaluación: {e}")
        
        if st.session_state.get("preguntas_examen"):
            respuestas_usuario = {}
            with st.form("formulario_evaluacion"):
                for idx, item in enumerate(st.session_state.preguntas_examen):
                    st.markdown(f"**Pregunta {idx+1}:** {item['pregunta']}")
                    respuestas_usuario[item['id']] = st.radio("Selecciona tu respuesta:", options=item['opciones'], key=f"p_{item['id']}")
                st.write("---")
                enviar_evaluacion = st.form_submit_button("Enviar Respuestas al Docente")
                
                if enviar_evaluacion:
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
                    
                    nota_final = (respuestas_correctas / total_preguntas) * 20
                    st.metric(label="Calificación de la Evaluación", value=f"{nota_final:.1f} / 20.0")
                    
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
