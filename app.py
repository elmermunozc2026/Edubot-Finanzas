import os
import re
import time
import random
import pandas as pd
import streamlit as st
import google.generativeai as genai

# ==============================================================================
# FUNCIÓN DE LIMPIEZA Y SANITIZACIÓN
# ==============================================================================
def sanitizar_texto_cfo(texto):
    """
    Extrae ÚNICAMENTE el bloque en español dirigido al estudiante.
    Elimina cualquier borrador en inglés tanto ANTES como DESPUÉS de la respuesta.
    """
    if not texto:
        return ""

    # 1. ENCONTRAR EL INICIO (Corta todo lo que esté ANTES del saludo en español)
    patron_inicio = re.search(r'\b(Estimado|Hola|Bienvenido|Entiendo|Respecto|Sobre|Como CFO)\b', texto, re.IGNORECASE)
    
    if patron_inicio:
        texto = texto[patron_inicio.start():].strip()

    # 2. ENCONTRAR EL FINAL (Corta todo lo que el modelo escriba en inglés DESPUÉS del texto)
    # Marcadres típicos donde el modelo empieza a autoevaluarse en inglés al final:
    patrones_corte_final = [
        r"\n\s*Wait\b", r"\n\s*Check\b", r"\n\s*Self-Correction", 
        r"\n\s*Final Polish", r"\n\s*Role:", r"\n\s*Constraint", 
        r"\n\s*Evaluation:", r"\n\s*Liquidity Analysis:"
    ]

    for patron in patrones_corte_final:
        corte = re.search(patron, texto, re.IGNORECASE)
        if corte:
            texto = texto[:corte.start()].strip()

    # 3. FILTRADO LÍNEA POR LÍNEA DE RESPALDO
    lineas = texto.split("\n")
    lineas_limpias = []
    palabras_basura_ingles = [
        "role:", "constraint", "case a:", "case b:", "case c:", "data:",
        "required content:", "language:", "greeting:", "evaluation:",
        "liquidity analysis:", "socratic questions:", "self-correction",
        "drafting", "acid test calculation", "check constraints", "wait,"
    ]

    for l in lineas:
        l_lower = l.strip().lower()
        if not any(b in l_lower for b in palabras_basura_ingles):
            lineas_limpias.append(l)

    return "\n".join(lineas_limpias).strip()
    
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

import os
import re
import time
import streamlit as st
import google.generativeai as genai

# ==========================================
#  FUNCIÓN DE LIMPIEZA DE METADATOS Y DRAFTS
# ==========================================

def sanitizar_texto_cfo(texto):
    """Limpia borradores internos y metadatos en inglés."""
    if not texto:
        return ""
    
    # Si hay un bloque de borrador/refinamiento, conservar la última parte
    for separador in ["Drafting the response:", "Refining:", "Response:", "Draft:"]:
        if separador in texto:
            texto = texto.split(separador)[-1]

    etiquetas_prohibidas = [
        "role:", "scenario:", "financial data:", "user question:", "rules:", 
        "step 1:", "step 2:", "step 3:", "applying the socratic", "drafting"
    ]
    
    lineas = texto.split("\n")
    lineas_limpias = [
        l for l in lineas 
        if not any(l.strip().lower().startswith(tag) for tag in etiquetas_prohibidas)
    ]
    
    resultado = "\n\n".join(lineas_limpias).strip()
    return resultado if resultado else texto.strip()
    
# ==========================================
#  FUNCIÓN DE CONEXIÓN CON CONTROL DE ERRORES
# ==========================================

def llamar_gemini_api(historial_mensajes, caso_info):
    """
    Llama a Gemini forzando una respuesta ejecutiva limpia en español.
    """
    system_instruction = (
        "Eres el CFO Corporativo de una empresa minera y Tutor Académico de Posgrado.\n"
        "TU ÚNICA TAREA es responder al estudiante EN ESPAÑOL. NO generes notas internas, "
        "ni revisiones, ni análisis en inglés antes o después de tu respuesta.\n\n"
        f"CASO EVALUADO: {caso_info['titulo']} ({caso_info['entorno']}).\n"
        f"DATOS CLAVE: Balance ({caso_info['balance_a2']}) | Resultados ({caso_info['resultados_a2']}).\n\n"
        "ESTRUCTURA OBLIGATORIA DE TU RESPUESTA:\n"
        "1. Inicia con 'Estimado estudiante,' o 'Estimado [Nombre],'.\n"
        "2. Valida sus aciertos en liquidez y operaciones.\n"
        "3. Analiza la NIC 2 / IAS 2 sobre el inventario (Costo vs. Valor Neto Realizable - VNR).\n"
        "4. Muestra el cálculo explícito de la Prueba Ácida: (Efectivo + Cuentas por Cobrar) / Pasivo Corriente.\n"
        "5. Cierra con 2 preguntas socráticas de toma de decisiones.\n"
        "TERMINA TU RESPUESTA INMEDIATAMENTE DESPUÉS DE LAS PREGUNTAS."
    )

    contents = []
    for m in historial_mensajes:
        role = "user" if m["role"] == "user" else "model"
        # Limpieza previa del historial enviado para no re-contaminar al modelo
        contenido = sanitizar_texto_cfo(m["content"]) if role == "model" else m["content"]
        contents.append({"role": role, "parts": [{"text": contenido}]})

    modelos_candidatos = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]
    
    ultimo_error = None

    for mod in modelos_candidatos:
        try:
            model = genai.GenerativeModel(
                model_name=mod,
                system_instruction=system_instruction
            )
            response = model.generate_content(
                contents,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Temperatura baja para evitar divagaciones/autoevaluaciones
                    max_output_tokens=1200
                )
            )
            if response and response.text:
                texto_limpio = sanitizar_texto_cfo(response.text)
                if texto_limpio:
                    return texto_limpio
        except Exception as e:
            ultimo_error = str(e)
            continue

    raise Exception(f"Error técnico en la llamadas: {ultimo_error}")

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
