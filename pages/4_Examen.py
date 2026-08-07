"""
CFO Agent IA - Página de Exámenes Mixtos
Tipos: opción múltiple, múltiple selección, texto libre
Con tiempo límite, anti-copia y anti-paste
"""
import streamlit as st
import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import require_auth, logout_user, init_auth
from tools.exam_tools import get_exam_questions, calculate_exam_score, EXAM_QUESTIONS
from memory.database import StudentMemory
from i18n.translations import t

st.set_page_config(
    page_title="CFO Agent IA — Examen",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS + JS: ANTI-COPIA, ANTI-PASTE, CHAT FIJO ──────────────────────────────
st.markdown("""
<style>
/* ── ANTI-COPIA en preguntas de examen ── */
.exam-question {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}
/* ── Estilo de preguntas ── */
.question-card {
    background: white; border-radius: 12px; padding: 20px;
    margin: 12px 0; box-shadow: 0 2px 8px rgba(31,78,121,0.10);
    border-left: 5px solid #2E75B6;
}
.question-type-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 11px; font-weight: bold; margin-bottom: 8px;
}
.type-opcion    { background: #E8F0FE; color: #1F4E79; }
.type-multiple  { background: #E8F5E9; color: #1E8449; }
.type-texto     { background: #FFF3E0; color: #E65100; }
/* ── Timer ── */
.timer-box {
    background: linear-gradient(135deg, #1F4E79, #2E75B6);
    border-radius: 12px; padding: 12px 20px; color: white;
    text-align: center; font-size: 24px; font-weight: bold;
}
.timer-warning { background: linear-gradient(135deg, #E65100, #FF6D00) !important; }
.timer-critical { background: linear-gradient(135deg, #B71C1C, #D32F2F) !important; }
/* ── Resultado ── */
.result-excellent { background: #F0FFF4; border: 2px solid #00AA44; border-radius: 12px; padding: 20px; }
.result-good      { background: #EEF2FF; border: 2px solid #2E75B6; border-radius: 12px; padding: 20px; }
.result-regular   { background: #FFFBF0; border: 2px solid #FFA500; border-radius: 12px; padding: 20px; }
.result-low       { background: #FFF0F0; border: 2px solid #FF4444; border-radius: 12px; padding: 20px; }
/* ── Sidebar logout ── */
.logout-btn { margin-top: 20px; }
</style>

<script>
// ── ANTI-COPIA: bloquear selección y copia en preguntas ──
document.addEventListener('DOMContentLoaded', function() {
    // Bloquear clic derecho en preguntas
    document.addEventListener('contextmenu', function(e) {
        if (e.target.closest('.exam-question')) {
            e.preventDefault();
            return false;
        }
    });
    // Bloquear Ctrl+C en preguntas
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
            const sel = window.getSelection();
            if (sel && sel.toString().length > 0) {
                const node = sel.anchorNode;
                if (node && node.parentElement && node.parentElement.closest('.exam-question')) {
                    e.preventDefault();
                    return false;
                }
            }
        }
    });
});

// ── ANTI-PASTE: bloquear pegar en textareas de examen ──
document.addEventListener('paste', function(e) {
    const target = e.target;
    if (target.tagName === 'TEXTAREA' &&
        (target.closest('.exam-text-answer') || target.getAttribute('data-exam') === 'true')) {
        e.preventDefault();
        e.stopPropagation();
        // Mostrar mensaje
        const msg = document.createElement('div');
        msg.style.cssText = 'position:fixed;top:20px;right:20px;background:#FF4444;color:white;padding:12px 20px;border-radius:8px;z-index:9999;font-weight:bold;';
        msg.textContent = '⛔ No se permite pegar texto en las respuestas del examen.';
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 3000);
        return false;
    }
});
</script>
""", unsafe_allow_html=True)

# ── AUTENTICACIÓN ─────────────────────────────────────────────────────────────
user = require_auth(allowed_roles=["alumno", "profesor", "admin"])
lang = st.session_state.get("lang", "es")
memory = StudentMemory()
student_id = user["email"].replace("@", "_").replace(".", "_")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/test-passed.png", width=60)
    st.title("📝 Exámenes CFO")
    st.caption(f"{'Alumno' if lang == 'es' else 'Student'}: **{user['name']}**")
    st.divider()

    # Selector de idioma
    idioma = st.radio("🌐", ["🇪🇸 Español", "🇺🇸 English"], horizontal=True,
                      index=0 if lang == "es" else 1, key="idioma_examen")
    new_lang = "en" if "English" in idioma else "es"
    if new_lang != lang:
        st.session_state["lang"] = new_lang
        st.rerun()

    st.divider()
    if st.button("🚪 Cerrar Sesión" if lang == "es" else "🚪 Sign Out",
                 use_container_width=True, type="secondary"):
        logout_user()
        st.switch_page("login.py")

# ── TEXTOS ────────────────────────────────────────────────────────────────────
TX = {
    "es": {
        "titulo": "📝 Centro de Exámenes",
        "config_titulo": "⚙️ Configurar Examen",
        "tema": "📚 Tema del examen:",
        "dificultad": "🎯 Nivel de dificultad:",
        "num_preguntas": "🔢 Número de preguntas:",
        "tiempo_pregunta": "⏱️ Tiempo por pregunta (min):",
        "tiempo_total": "⏱️ Tiempo total del examen (min):",
        "iniciar": "🚀 Iniciar Examen",
        "instrucciones": "📋 Instrucciones",
        "inst1": "Lee cada pregunta cuidadosamente antes de responder.",
        "inst2": "No se permite copiar las preguntas ni pegar respuestas.",
        "inst3": "El tiempo corre desde que inicias el examen.",
        "inst4": "Puedes navegar entre preguntas antes de enviar.",
        "inst5": "Una vez enviado, no puedes modificar tus respuestas.",
        "enviar": "✅ Enviar Examen",
        "tiempo_restante": "⏱️ Tiempo restante:",
        "tiempo_agotado": "⏰ ¡Tiempo agotado! El examen se envió automáticamente.",
        "pregunta": "Pregunta",
        "de": "de",
        "tipo_opcion": "Opción múltiple",
        "tipo_multiple": "Múltiple selección",
        "tipo_texto": "Respuesta escrita",
        "selecciona_una": "Selecciona una respuesta:",
        "selecciona_varias": "Selecciona todas las correctas:",
        "escribe_respuesta": "Escribe tu respuesta aquí (no se permite pegar texto):",
        "resultado_titulo": "🎯 Resultado del Examen",
        "calificacion": "Calificación",
        "nivel": "Nivel",
        "puntos": "Puntos",
        "detalle": "📊 Ver detalle por pregunta",
        "correcto": "✅ Correcto",
        "incorrecto": "❌ Incorrecto",
        "parcial": "🟡 Parcial",
        "tu_respuesta": "Tu respuesta:",
        "respuesta_correcta": "Respuesta correcta:",
        "explicacion": "💡 Explicación:",
        "nuevo_examen": "🔄 Nuevo Examen",
        "advertencia_tiempo": "⚠️ ¡Menos de 5 minutos!",
        "tiempo_por_pregunta": "Tiempo por pregunta:",
        "tiempo_examen_total": "Tiempo total del examen:",
        "minutos": "minutos",
        "segundos": "segundos",
        "no_pegar": "⛔ No se permite pegar texto en las respuestas.",
    },
    "en": {
        "titulo": "📝 Exam Center",
        "config_titulo": "⚙️ Configure Exam",
        "tema": "📚 Exam topic:",
        "dificultad": "🎯 Difficulty level:",
        "num_preguntas": "🔢 Number of questions:",
        "tiempo_pregunta": "⏱️ Time per question (min):",
        "tiempo_total": "⏱️ Total exam time (min):",
        "iniciar": "🚀 Start Exam",
        "instrucciones": "📋 Instructions",
        "inst1": "Read each question carefully before answering.",
        "inst2": "Copying questions or pasting answers is not allowed.",
        "inst3": "Time starts when you begin the exam.",
        "inst4": "You can navigate between questions before submitting.",
        "inst5": "Once submitted, you cannot modify your answers.",
        "enviar": "✅ Submit Exam",
        "tiempo_restante": "⏱️ Time remaining:",
        "tiempo_agotado": "⏰ Time's up! The exam was automatically submitted.",
        "pregunta": "Question",
        "de": "of",
        "tipo_opcion": "Multiple choice",
        "tipo_multiple": "Multiple selection",
        "tipo_texto": "Written answer",
        "selecciona_una": "Select one answer:",
        "selecciona_varias": "Select all correct answers:",
        "escribe_respuesta": "Write your answer here (pasting is not allowed):",
        "resultado_titulo": "🎯 Exam Result",
        "calificacion": "Grade",
        "nivel": "Level",
        "puntos": "Points",
        "detalle": "📊 View question details",
        "correcto": "✅ Correct",
        "incorrecto": "❌ Incorrect",
        "parcial": "🟡 Partial",
        "tu_respuesta": "Your answer:",
        "respuesta_correcta": "Correct answer:",
        "explicacion": "💡 Explanation:",
        "nuevo_examen": "🔄 New Exam",
        "advertencia_tiempo": "⚠️ Less than 5 minutes!",
        "tiempo_por_pregunta": "Time per question:",
        "tiempo_examen_total": "Total exam time:",
        "minutos": "minutes",
        "segundos": "seconds",
        "no_pegar": "⛔ Pasting text in answers is not allowed.",
    },
}
T = TX[lang]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title(T["titulo"])
st.caption(f"**{user['name']}** | {user['role'].title()} | Sector: {user.get('sector', 'mining')}")
st.divider()

# ── ESTADO DEL EXAMEN ─────────────────────────────────────────────────────────
if "exam_state" not in st.session_state:
    st.session_state.exam_state = "config"   # config | running | finished
if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []
if "exam_answers" not in st.session_state:
    st.session_state.exam_answers = {}
if "exam_start_time" not in st.session_state:
    st.session_state.exam_start_time = None
if "exam_result" not in st.session_state:
    st.session_state.exam_result = None
if "exam_config" not in st.session_state:
    st.session_state.exam_config = {}

# ─────────────────────────────────────────────────────────────────────────────
# FASE 1: CONFIGURACIÓN DEL EXAMEN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.exam_state == "config":

    col_config, col_inst = st.columns([1, 1])

    with col_config:
        st.subheader(T["config_titulo"])

        topic_options = {
            "ratios_financieros": "📊 Ratios Financieros" if lang == "es" else "📊 Financial Ratios",
            "flujo_caja":         "💰 Flujo de Caja" if lang == "es" else "💰 Cash Flow",
            "presupuesto_capex":  "📈 Presupuesto y CAPEX" if lang == "es" else "📈 Budget & CAPEX",
            "riesgos":            "⚠️ Gestión de Riesgos" if lang == "es" else "⚠️ Risk Management",
        }
        difficulty_options = {
            "basico":      "🟡 Básico" if lang == "es" else "🟡 Basic",
            "intermedio":  "🔵 Intermedio" if lang == "es" else "🔵 Intermediate",
            "avanzado":    "🟢 Avanzado" if lang == "es" else "🟢 Advanced",
        }

        topic = st.selectbox(T["tema"], list(topic_options.keys()),
                             format_func=lambda x: topic_options[x])
        difficulty = st.selectbox(T["dificultad"], list(difficulty_options.keys()),
                                  format_func=lambda x: difficulty_options[x], index=1)
        num_q = st.slider(T["num_preguntas"], min_value=3, max_value=10, value=5)

        st.divider()
        st.markdown(f"**⏱️ {'Configuración de tiempo:' if lang == 'es' else 'Time configuration:'}**")
        tiempo_por_pregunta = st.number_input(
            T["tiempo_pregunta"], min_value=1, max_value=10, value=3
        )
        tiempo_total = st.number_input(
            T["tiempo_total"], min_value=5, max_value=120,
            value=num_q * tiempo_por_pregunta
        )

        st.info(f"""
        ⏱️ **{T['tiempo_por_pregunta']}** {tiempo_por_pregunta} {T['minutos']}
        ⏱️ **{T['tiempo_examen_total']}** {tiempo_total} {T['minutos']}
        """)

        if st.button(T["iniciar"], type="primary", use_container_width=True):
            questions = get_exam_questions(
                topic=topic,
                difficulty=difficulty,
                lang=lang,
                num_questions=num_q,
                mix_types=True,
            )
            if questions:
                st.session_state.exam_questions = questions
                st.session_state.exam_answers = {}
                st.session_state.exam_start_time = time.time()
                st.session_state.exam_config = {
                    "topic": topic,
                    "difficulty": difficulty,
                    "num_questions": num_q,
                    "tiempo_por_pregunta_seg": tiempo_por_pregunta * 60,
                    "tiempo_total_seg": tiempo_total * 60,
                }
                st.session_state.exam_state = "running"
                st.rerun()
            else:
                st.warning("No hay preguntas disponibles para esta configuración." if lang == "es"
                           else "No questions available for this configuration.")

    with col_inst:
        st.subheader(T["instrucciones"])
        instrucciones = [T["inst1"], T["inst2"], T["inst3"], T["inst4"], T["inst5"]]
        for i, inst in enumerate(instrucciones, 1):
            st.markdown(f"**{i}.** {inst}")

        st.divider()
        st.markdown(f"**{'📊 Tipos de preguntas:' if lang == 'es' else '📊 Question types:'}**")
        tipos = [
            ("🔵", T["tipo_opcion"],   "Una sola respuesta correcta" if lang == "es" else "One correct answer"),
            ("🟢", T["tipo_multiple"], "Varias respuestas correctas" if lang == "es" else "Multiple correct answers"),
            ("🟠", T["tipo_texto"],    "Respuesta escrita libre" if lang == "es" else "Free written answer"),
        ]
        for icon, tipo, desc in tipos:
            st.markdown(f"{icon} **{tipo}**: {desc}")

        st.divider()
        st.markdown(f"**{'🔒 Restricciones de seguridad:' if lang == 'es' else '🔒 Security restrictions:'}**")
        restricciones = [
            "⛔ No se puede copiar el texto de las preguntas" if lang == "es" else "⛔ Cannot copy question text",
            "⛔ No se puede pegar texto en las respuestas" if lang == "es" else "⛔ Cannot paste text in answers",
            "⏰ El examen se envía automáticamente al agotar el tiempo" if lang == "es" else "⏰ Exam auto-submits when time runs out",
        ]
        for r in restricciones:
            st.markdown(f"- {r}")

# ─────────────────────────────────────────────────────────────────────────────
# FASE 2: EXAMEN EN CURSO
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.exam_state == "running":

    questions = st.session_state.exam_questions
    config = st.session_state.exam_config
    elapsed = time.time() - st.session_state.exam_start_time
    remaining = max(0, config["tiempo_total_seg"] - elapsed)

    # ── TIMER ─────────────────────────────────────────────────────────────────
    mins = int(remaining // 60)
    secs = int(remaining % 60)
    timer_class = "timer-box"
    if remaining < 300:
        timer_class += " timer-warning"
    if remaining < 60:
        timer_class += " timer-critical"

    col_timer, col_progress = st.columns([1, 3])
    with col_timer:
        st.markdown(f"""
        <div class="{timer_class}">
            {T['tiempo_restante']}<br>
            {mins:02d}:{secs:02d}
        </div>""", unsafe_allow_html=True)
    with col_progress:
        answered = len([a for a in st.session_state.exam_answers.values() if a is not None])
        st.progress(answered / len(questions), text=f"{answered}/{len(questions)} {'respondidas' if lang == 'es' else 'answered'}")
        if remaining < 300:
            st.warning(T["advertencia_tiempo"])

    # Auto-submit si se agota el tiempo
    if remaining <= 0:
        st.warning(T["tiempo_agotado"])
        result = calculate_exam_score(questions, st.session_state.exam_answers)
        st.session_state.exam_result = result
        st.session_state.exam_state = "finished"
        memory.save_evaluation(
            student_id=student_id,
            topic=config["topic"],
            score=result["calificacion_10"],
            max_score=10.0,
            difficulty=config["difficulty"],
        )
        st.rerun()

    st.divider()

    # ── PREGUNTAS ─────────────────────────────────────────────────────────────
    with st.form("exam_form"):
        for i, q in enumerate(questions):
            tipo = q.get("tipo", "opcion_multiple")
            puntos = q.get("puntos", 1)
            tiempo_q = q.get("tiempo_segundos", 90)

            # Badge de tipo
            badge_class = {"opcion_multiple": "type-opcion", "multiple_seleccion": "type-multiple", "texto_libre": "type-texto"}.get(tipo, "type-opcion")
            badge_label = {"opcion_multiple": T["tipo_opcion"], "multiple_seleccion": T["tipo_multiple"], "texto_libre": T["tipo_texto"]}.get(tipo, "")

            st.markdown(f"""
            <div class="question-card">
                <span class="question-type-badge {badge_class}">{badge_label}</span>
                <span style="float:right;font-size:12px;color:#7F7F7F">
                    {puntos} {'pt' if puntos == 1 else 'pts'} | ⏱️ {tiempo_q//60}:{tiempo_q%60:02d}
                </span>
                <div class="exam-question">
                    <strong>{T['pregunta']} {i+1} {T['de']} {len(questions)}:</strong><br><br>
                    {q['pregunta']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Respuesta según tipo
            if tipo == "opcion_multiple":
                opciones = q.get("opciones", [])
                answer = st.radio(
                    T["selecciona_una"],
                    options=range(len(opciones)),
                    format_func=lambda x: opciones[x],
                    key=f"q_{q['id']}",
                    index=None,
                )
                st.session_state.exam_answers[q["id"]] = answer

            elif tipo == "multiple_seleccion":
                opciones = q.get("opciones", [])
                st.markdown(f"*{T['selecciona_varias']}*")
                selected = []
                for j, opcion in enumerate(opciones):
                    checked = st.checkbox(opcion, key=f"q_{q['id']}_opt_{j}")
                    if checked:
                        selected.append(j)
                st.session_state.exam_answers[q["id"]] = selected

            elif tipo == "texto_libre":
                # Textarea con atributo data-exam para el JS anti-paste
                answer_text = st.text_area(
                    T["escribe_respuesta"],
                    key=f"q_{q['id']}_text",
                    height=120,
                    help=T["no_pegar"],
                    placeholder="Escribe tu respuesta aquí..." if lang == "es" else "Write your answer here...",
                )
                st.session_state.exam_answers[q["id"]] = answer_text

            st.markdown("---")

        # Botón de envío
        submitted = st.form_submit_button(T["enviar"], type="primary", use_container_width=True)

    if submitted:
        result = calculate_exam_score(questions, st.session_state.exam_answers)
        st.session_state.exam_result = result
        st.session_state.exam_state = "finished"
        memory.save_evaluation(
            student_id=student_id,
            topic=config["topic"],
            score=result["calificacion_10"],
            max_score=10.0,
            difficulty=config["difficulty"],
        )
        st.rerun()

    # Auto-refresh cada 30 segundos para actualizar el timer
    st.markdown("""
    <script>
    setTimeout(function() { window.location.reload(); }, 30000);
    </script>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FASE 3: RESULTADO DEL EXAMEN
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.exam_state == "finished":

    result = st.session_state.exam_result
    score = result["calificacion_10"]
    nivel = result["nivel"]

    # Clase CSS según calificación
    result_class = (
        "result-excellent" if score >= 9 else
        "result-good"      if score >= 7 else
        "result-regular"   if score >= 5 else
        "result-low"
    )
    emoji = "🏆" if score >= 9 else "✅" if score >= 7 else "📚" if score >= 5 else "💪"

    st.markdown(f"""
    <div class="{result_class}">
        <h2 style="text-align:center">{emoji} {T['resultado_titulo']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # KPIs del resultado
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"📊 {T['calificacion']}", f"{score}/10")
    with col2:
        st.metric(f"🎯 {T['nivel']}", nivel)
    with col3:
        st.metric(f"💯 {T['puntos']}", f"{result['puntos_obtenidos']}/{result['puntos_totales']}")
    with col4:
        st.metric("📈 %", f"{result['porcentaje']}%")

    st.divider()

    # Detalle por pregunta
    with st.expander(T["detalle"], expanded=True):
        for i, det in enumerate(result["resultados_detalle"], 1):
            is_correct = det["es_correcto"]
            status = T["correcto"] if is_correct else T["incorrecto"]
            bg = "#F0FFF4" if is_correct else "#FFF0F0"

            st.markdown(f"""
            <div style="background:{bg};border-radius:8px;padding:12px;margin:8px 0">
                <strong>{T['pregunta']} {i}:</strong> {status}<br>
                <em class="exam-question">{det['pregunta'][:100]}...</em>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**{T['tu_respuesta']}** {det['respuesta_alumno']}")
            with col_b:
                st.markdown(f"**{T['respuesta_correcta']}** {det['respuesta_correcta']}")

            if det.get("feedback"):
                st.info(f"{T['explicacion']} {det['feedback']}")

    st.divider()

    # Botón nuevo examen
    if st.button(T["nuevo_examen"], type="primary", use_container_width=True):
        for key in ["exam_state", "exam_questions", "exam_answers",
                    "exam_start_time", "exam_result", "exam_config"]:
            st.session_state.pop(key, None)
        st.rerun()
