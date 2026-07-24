import streamlit as st
import pandas as pd
import json
import random
import google.generativeai as genai

# ==========================================
#      CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CFO Edubot - Evaluación Dinámica", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ACCESO SEGURO A LA API KEY
if "GEMINI_API_KEY" in st.secrets:
    api_key_segura = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key_segura)
else:
    st.error("Error de configuración: No se encontró la API Key en los secretos del servidor.")
    st.stop()

# ==========================================
#  INICIALIZACIÓN DEL ESTADO DE SESIÓN
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "nombre_estudiante" not in st.session_state:
    st.session_state.nombre_estudiante = ""

# ==========================================
#      CONTROL DE ACCESO (LOGIN OBLIGATORIO)
# ==========================================
if not st.session_state.autenticado:
    st.title("🔐 Acceso Autorizado - Edubot Finanzas")
    st.write("Por favor, introduce tus credenciales de estudiante para ingresar a la plataforma.")
    
    with st.form("formulario_login"):
        correo_input = st.text_input("Correo electrónico institucional:").strip().lower()
        password_input = st.text_input("Contraseña temporal del curso:", type="password")
        boton_ingresar = st.form_submit_button("Ingresar al Edubot")
        
        if boton_ingresar:
            try:
                password_valida = st.secrets["accesos_alumnos"]["password_temporal"]
                correos_validos = [c.lower() for c in st.secrets["accesos_alumnos"]["correos_autorizados"]]
                
                if correo_input in correos_validos and password_input == password_valida:
                    st.session_state.autenticado = True
                    nombre_defecto = correo_input.split("@")[0].replace(".", " ").title()
                    st.session_state.nombre_estudiante = nombre_defecto
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("El correo no está registrado como autorizado o la contraseña es incorrecta.")
            except Exception as e:
                st.error("Error al verificar las credenciales.")
    st.stop()

# ==========================================
#     BANCO DE CASOS MINEROS
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

if "caso_seleccionado" not in st.session_state:
    st.session_state.caso_seleccionado = random.choice(CASOS_MINEROS)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "preguntas_examen" not in st.session_state:
    st.session_state.preguntas_examen = None

# ==========================================
#  FUNCIÓN DE CONEXIÓN A PRUEBA DE BORRADORES
# ==========================================
def llamar_gemini_api(historial_mensajes, caso_info):
    """Llama a Gemini aislando por completo los bloques de pensamiento (thinking) en inglés."""
    
    system_instruction = (
        f"Eres el Director de Finanzas (CFO) Corporativo de una empresa minera y Tutor Académico. "
        f"Estás evaluando al estudiante en Análisis Financiero.\n"
        f"Escenario: {caso_info['titulo']} - {caso_info['entorno']}.\n"
        f"Datos Financieros: {caso_info['balance_a2']} | {caso_info['resultados_a2']}.\n\n"
        "REGLAS ABSOLUTAS DE RESPUESTA:\n"
        "1. Responde ÚNICAMENTE en español y de forma directa al estudiante.\n"
        "2. Asume tu rol de CFO ('yo'). Sé profesional y utiliza el método socrático.\n"
        "3. PROHIBIDO IMPRIMIR NOTAS DE RAZONAMIENTO INTERNO, 'Role:', 'Goal:', 'Context:', 'Scenario:' O FRASES EN INGLÉS."
    )

    # Formatear el historial garantizando roles limpios
    contents = []
    for m in historial_mensajes:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [m["content"]]})

    modelos_disponibles = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]

    for mod in modelos_disponibles:
        try:
            model = genai.GenerativeModel(
                model_name=mod,
                system_instruction=system_instruction
            )
            
            # Forzar la generación sin bloques de pensamiento
            response = model.generate_content(
                contents,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=600
                )
            )
            
            # Extraer únicamente el texto de respuesta al usuario
            texto_limpio = ""
            if hasattr(response, 'candidates') and response.candidates:
                partes = response.candidates[0].content.parts
                for p in partes:
                    # Ignorar cualquier objeto etiquetado como pensamiento interno
                    if getattr(p, 'thought', False):
                        continue
                    if hasattr(p, 'text') and p.text:
                        texto_limpio += p.text

            if not texto_limpio.strip():
                texto_limpio = response.text.strip()

            # Filtro secundario estricto por palabras clave de metadatos
            if any(k in texto_limpio for k in ["Role:", "Goal:", "Context:", "Scenario:", "Student's Input:", "Missing the"]):
                lineas = texto_limpio.split("\n")
                lineas_validas = [
                    l for l in lineas 
                    if not any(k in l for k in ["Role:", "Goal:", "Context:", "Scenario:", "Financial Data:", "Student's Input:", "Missing the", "Step 1:", "Step 2:", "Step 3:"])
                ]
                texto_limpio = "\n".join(lineas_validas).strip()

            return texto_limpio

        except Exception:
            continue

    # Fallback dinámico si los modelos principales presentan interrupción
    try:
        modelos_activos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m_activo in modelos_activos:
            try:
                model = genai.GenerativeModel(model_name=m_activo, system_instruction=system_instruction)
                response = model.generate_content(contents, generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=600))
                return response.text.strip()
            except Exception:
                continue
    except Exception as e:
        raise Exception(f"Error al conectar con la API: {e}")

    raise Exception("No hay modelos disponibles en este momento.")

# ==========================================
#     PANEL LATERAL
# ==========================================
nombre_estudiante = st.sidebar.text_input("Nombre del Estudiante:", value=st.session_state.nombre_estudiante)
st.session_state.nombre_estudiante = nombre_estudiante

with st.sidebar:
    st.write("---")
    if st.button("🔄 Cambiar de Caso (Reiniciar)", use_container_width=True):
        st.session_state.pop("caso_seleccionado", None)
        st.session_state.pop("messages", None)
        st.session_state.pop("preguntas_examen", None)
        st.rerun()

# ==========================================
#     DISTRIBUCIÓN DE PANTALLA
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
            # Mensaje de bienvenida inicial (se muestra en pantalla pero no contamina el historial)
            st.chat_message("assistant").write(f"Hola {nombre_estudiante}. Soy el CFO de la minera. {caso_actual['mensaje_inicial']}")
            
            # Historial interactivo
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if user_input := st.chat_input("Escribe tu propuesta al CFO..."):
            with chat_container:
                st.chat_message("user").write(user_input)
                
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                with st.spinner("El CFO evalúa tu respuesta..."):
                    respuesta_texto = llamar_gemini_api(st.session_state.messages, caso_actual)
                    
                with chat_container:
                    st.chat_message("assistant").write(respuesta_texto)
                    
                st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
                
            except Exception as e:
                st.error(f"Error en la interacción: {e}")
                
    with tab2:
        st.subheader("Evaluación Escrita a Medida")
        st.write("El CFO generará preguntas de opción múltiple basadas en la discusión realizada.")
        
        if st.button("Generar mi Examen Único"):
            prompt_evaluacion = (
                "Genera 3 preguntas de opción múltiple basadas en este caso minero y discusión. "
                "Responde ÚNICAMENTE con un JSON válido con esta estructura exacta, sin markdown ni ```json:\n"
                '{"preguntas": [{"id": 1, "pregunta": "...", "opciones": ["A", "B", "C", "D"], "correcta": "opcion exacta"}]}'
            )
            try:
                with st.spinner("El CFO está redactando tus preguntas..."):
                    # Limpiamos las claves anteriores del formulario para no dejar respuestas pre-seleccionadas
                    for k in list(st.session_state.keys()):
                        if k.startswith("p_"):
                            del st.session_state[k]
                            
                    historial_eval = st.session_state.messages + [{"role": "user", "content": prompt_evaluacion}]
                    response_json = llamar_gemini_api(historial_eval, caso_actual)
                    response_json = response_json.replace("```json", "").replace("```", "").strip()
                    st.session_state.preguntas_examen = json.loads(response_json)["preguntas"]
                    st.success("¡Examen generado exitosamente!")
            except Exception as e:
                st.error(f"Error al estructurar la evaluación: {e}")
        
        if st.session_state.get("preguntas_examen"):
            respuestas_usuario = {}
            with st.form("formulario_evaluacion"):
                for idx, item in enumerate(st.session_state.preguntas_examen):
                    st.markdown(f"**Pregunta {idx+1}:** {item['pregunta']}")
                    # index=None hace que NINGUNA alternativa aparezca marcada por defecto
                    respuestas_usuario[item['id']] = st.radio(
                        "Selecciona tu respuesta:", 
                        options=item['opciones'], 
                        index=None, 
                        key=f"p_{item['id']}"
                    )
                st.write("---")
                enviar_evaluacion = st.form_submit_button("Enviar Respuestas al Docente")
                
                if enviar_evaluacion:
                    # Validar si el alumno dejó preguntas sin responder
                    if any(v is None for v in respuestas_usuario.values()):
                        st.warning("Por favor, responde todas las preguntas antes de enviar.")
                    else:
                        respuestas_correctas = sum(1 for item in st.session_state.preguntas_examen if respuestas_usuario[item['id']] == item['correcta'])
                        total_preguntas = len(st.session_state.preguntas_examen)
                        nota_final = (respuestas_correctas / total_preguntas) * 20
                        st.metric(label="Calificación Obtendida", value=f"{nota_final:.1f} / 20.0")
