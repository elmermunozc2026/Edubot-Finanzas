# ==============================================================================
# 1. IMPORTS
# ==============================================================================

import os
import re
import time
import random
import json
import pandas as pd
import streamlit as st
import google.generativeai as genai

# Configurar la API Key desde st.secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Falta la clave GEMINI_API_KEY en st.secrets")
# ==============================================================================
# 2. FUNCIONES DE APOYO Y UTILIDADES
# ==============================================================================
def obtener_nombre_desde_email(email):
    """
    Extrae un nombre presentable a partir de un correo electrónico.
    Ejemplo: 'elmer.munoz@gmail.com' -> 'Elmer Muñoz' (o 'Elmer Munoz')
    """
    if not email or "@" not in email:
        return "Estudiante"
    
    # 1. Tomar solo la parte anterior al @
    usuario = email.split("@")[0]
    
    # 2. Reemplazar puntos, guiones bajos o guiones por espacios
    partes = re.split(r'[\._\-]', usuario)
    
    # 3. Capitalizar cada parte (ej: 'elmer' -> 'Elmer')
    nombre_formateado = " ".join([p.capitalize() for p in partes if p and not p.isdigit()])
    
    return nombre_formateado if nombre_formateado else "Estudiante"

# ==============================================================================
# 3.FUNCIÓN DE LIMPIEZA Y SANITIZACIÓN
# ==============================================================================
def sanitizar_texto_cfo(texto, nombre_estudiante="Estudiante"):
    if not texto:
        return ""

    primer_nombre = nombre_estudiante.split()[0] if nombre_estudiante else "Estudiante"

    patrones_inicio = [
        rf'Estimado\s+{re.escape(nombre_estudiante)}',
        rf'Estimado\s+{re.escape(primer_nombre)}',
        r'Estimado\s+estudiante',
        r'Estimado\b', r'Hola\b', r'Bienvenido\b'
    ]

    posicion_inicio = -1
    for patron in patrones_inicio:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            if posicion_inicio == -1 or match.start() < posicion_inicio:
                posicion_inicio = match.start()

    if posicion_inicio != -1:
        texto = texto[posicion_inicio:].strip()

    patrones_corte_final = [
        r"\n\s*Wait\b", r"\n\s*Check\b", r"\n\s*Self-Correction",
        r"\n\s*Final Polish", r"\n\s*Role:", r"\n\s*Constraint",
        r"\n\s*Evaluation:", r"\n\s*Liquidity Analysis:", r"\n\s*Check Constraints"
    ]

    for patron in patrones_corte_final:
        corte = re.search(patron, texto, re.IGNORECASE)
        if corte:
            texto = texto[:corte.start()].strip()

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
#  4.INICIALIZACIÓN DEL ESTADO DE SESIÓN
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "nombre_estudiante" not in st.session_state:
    st.session_state.nombre_estudiante = ""

# ==========================================
#  5.CONTROL DE ACCESO (LOGIN OBLIGATORIO)
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
#  FUNCIÓN DE CONEXIÓN CON CONTROL DE ERRORES
# ==========================================

def llamar_gemini_api(historial_mensajes, caso_actual, nombre_estudiante, modo="breve"):
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("No se encontró la variable GEMINI_API_KEY.")

    genai.configure(api_key=api_key)

    if modo == "breve":
        system_instruction = (
            f"Eres elCFO de una empresa minera transnacional y tienes experiencia amplia ( 30 años) en la gran minería, mediana minería y pequeña minería (Minería de tajo abierto y subterránea) y un profesor universitario de Finanzas. Responde en español y comienza con "
            f"'Estimado {nombre_estudiante},'. "

            "Da una respuesta breve, clara y pedagógica. "

            "Incluye únicamente: "
            "1) saludo, "
            "2) validación breve, "
            "3) un cálculo corto, "
            "4) una recomendación principal, "
            "5) una pregunta final. "
    
            "Escribe únicamente en texto plano. "
            "No utilices LaTeX. "
            "No utilices Markdown matemático. "
            "No utilices comandos como \\text{}, \\frac{}, \\left o \\right."
        )
        max_tokens = 900
    else:
        system_instruction = (
            f"Eres el CFO de una empresa minera transnacional y tienes experiencia amplia ( 30 años) en la gran minería, mediana minería y pequeña minería (Minería de tajo abierto y subterránea) y un profesor universitario de Finanzas. "
            f"Responde en español y comienza con 'Estimado {nombre_estudiante},'. "
    
            "Desarrolla una explicación completa y pedagógica utilizando esta estructura: "
    
            "1. Resumen ejecutivo. "
            "2. Análisis financiero paso a paso. "
            "3. Desarrollo de los cálculos mostrando cada operación en texto plano. "
            "4. Interpretación financiera. "
            "5. Relación con NIC/NIIF cuando corresponda. "
            "6. Riesgos identificados. "
            "7. Recomendaciones del CFO. "
            "8. Dos preguntas socráticas para el estudiante. "
    
            "Utiliza únicamente texto plano. "
            "No utilices LaTeX. "
            "No utilices Markdown matemático. "
            "No escribas ecuaciones entre $...$. "
            "No utilices \\text{}, \\frac{}, \\left, \\right, \\( \\) o \\[ \\]. "
    
            "Cuando necesites realizar cálculos, escríbelos así: "
            "'Razón Corriente = Activo Corriente / Pasivo Corriente = 2,500 / 1,800 = 1.39'."
        )
        max_tokens = 4096

    contents = []
    for m in historial_mensajes:
        role = "user" if m["role"] == "user" else "model"
        contenido = m["content"] if role == "user" else sanitizar_texto_cfo(m["content"], nombre_estudiante)
        if contenido.strip():
            contents.append({
                "role": role,
                "parts": [{"text": contenido.strip()}]
            })

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            system_instruction=system_instruction
        )

        response = model.generate_content(
            contents,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": max_tokens
            }
        )

        return sanitizar_texto_cfo(response.text, nombre_estudiante)

    except Exception as e:
        raise Exception(f"Error de Gemini: {e}")


   
    
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
#      DISTRIBUCIÓN DE PANTALLA
# ==========================================
col_datos, col_interactiva = st.columns([0.4, 0.6])

# Aseguramos la variable local por si acaso no viniera definida
nombre_estudiante = st.session_state.get("nombre_estudiante", "Estudiante")

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
            respuesta_texto = llamar_gemini_api(
                st.session_state.messages,
                caso_actual,
                nombre_estudiante,
                modo="breve"
            )

        with chat_container:
            st.chat_message("assistant").write(respuesta_texto)

        st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
        st.session_state.ultima_respuesta_breve = respuesta_texto

    except Exception as e:
        st.error(f"Error en la interacción: {e}")

if st.session_state.get("ultima_respuesta_breve"):
    if st.button("Ampliar explicación", use_container_width=True):

        # Construimos un historial corto para la ampliación
        historial_ampliacion = [
            st.session_state.messages[-2],   # Última pregunta del estudiante
            st.session_state.messages[-1],   # Última respuesta breve del CFO
            {
                "role": "user",
                "content": (
                    "Amplía únicamente la respuesta anterior. "
                    "No la repitas desde el inicio. "
                    "Continúa desarrollando el análisis financiero con mayor profundidad. "
                    "Explica los cálculos paso a paso y fundamenta las recomendaciones."
                )
            }
        ]

        try:
            with st.spinner("El CFO amplía el análisis..."):
                respuesta_larga = llamar_gemini_api(
                    historial_ampliacion,
                    caso_actual,
                    nombre_estudiante,
                    modo="amplio"
                )

            with chat_container:
                st.chat_message("assistant").write(respuesta_larga)

            st.session_state.messages.append({
                "role": "assistant",
                "content": respuesta_larga
            })

            st.session_state.ultima_respuesta_breve = None

        except Exception as e:
            st.error(f"Error al ampliar la explicación: {e}")
                          
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
                    # CAMBIO 2: Pasamos el nombre del estudiante también aquí
                    response_json = llamar_gemini_api(
                        historial_eval, 
                        caso_actual, 
                        nombre_estudiante
                    )
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

# =========================================================
# PIE DE PÁGINA / LATERAL: BOTÓN DE CERRAR SESIÓN
# =========================================================
import streamlit as st

# 1. Definir el botón de cerrar sesión en la consola lateral
def mostrar_boton_logout():
    with st.sidebar:
        st.markdown("---")  # Línea separadora
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            # A. Limpiar las variables de estado que guardan la sesión del usuario
            st.session_state.clear()
            
            # B. Si tienes variables específicas, también puedes borrarlas manualmente:
            # st.session_state["messages"] = []
            # st.session_state["usuario_autenticado"] = False
            
            # C. Recargar la aplicación para regresar al inicio
            st.rerun()

# Ejemplo de uso dentro de tu app:
mostrar_boton_logout()

