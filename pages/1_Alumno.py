"""
CFO Agent IA - Página del Alumno con Autenticación y Chat Fijo
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import CFOOrchestrator
from memory.database import StudentMemory
from prompts.system_prompts import get_greeting_prompt
from auth.auth_manager import require_auth, logout_user, init_auth
from tools.exam_tools import get_random_diagnostic_questions
from i18n.translations import t, SECTORS, STUDENT_LEVELS, PROGRAM_TOPICS

st.set_page_config(
    page_title="CFO Agent IA — Alumno",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: CHAT FIJO EN LA PARTE INFERIOR + ESTILOS ────────────────────────────
st.markdown("""
<style>
/* ── CHAT INPUT FIJO EN LA PARTE INFERIOR ── */
section[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    z-index: 999 !important;
    background: white !important;
    padding: 12px 20px !important;
    border-top: 2px solid #E0E8F0 !important;
    box-shadow: 0 -4px 12px rgba(31,78,121,0.10) !important;
}
/* Espacio para que el historial no quede tapado por el input fijo */
.main .block-container {
    padding-bottom: 100px !important;
}
/* ── TARJETAS DE MÉTRICAS ── */
.metric-card  { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:12px;
                padding:16px; color:white; text-align:center; margin:4px; }
.metric-value { font-size:28px; font-weight:bold; }
.metric-label { font-size:12px; opacity:0.85; }
/* ── SELECTOR DE IDIOMA ── */
.lang-selector{ background:#EEF2F7; border-radius:12px; padding:10px; margin-bottom:12px; }
/* ── BOTÓN LOGOUT ── */
.logout-section { margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# ── AUTENTICACIÓN ─────────────────────────────────────────────────────────────
user = require_auth(allowed_roles=["alumno", "admin"])
lang = st.session_state.get("lang", "es")
student_id = user["email"].replace("@", "_").replace(".", "_")
sector = user.get("sector", "mining")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Selector de idioma
    st.markdown('<div class="lang-selector">', unsafe_allow_html=True)
    idioma = st.radio(
        t("language_selector", "es"),
        ["🇪🇸 Español", "🇺🇸 English"],
        horizontal=True,
        key="idioma_alumno",
        index=0 if lang == "es" else 1,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    new_lang = "en" if "English" in idioma else "es"
    if new_lang != lang:
        for key in ["orchestrator_alumno", "messages_alumno", "lang_alumno"]:
            st.session_state.pop(key, None)
        st.session_state["lang"] = new_lang
        st.rerun()

    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=60)
    st.title("🎓 CFO Agent IA")
    st.caption(f"{'Módulo Educativo' if lang == 'es' else 'Educational Module'}")
    st.divider()

    # Info del usuario
    st.markdown(f"👤 **{user['name']}**")
    st.caption(f"📧 {user['email']}")
    st.caption(f"🏭 {SECTORS[lang].get(sector, sector)}")
    st.divider()

    # Progreso del alumno
    memory = StudentMemory()
    ctx = memory.get_context(student_id, n=20)
    avg = ctx.get("avg_score", 0)
    level = ctx.get("level", "basico")
    interactions = ctx.get("total_interactions", 0)

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg:.1f}/10</div>
        <div class="metric-label">{t("alumno_promedio", lang)}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(t("alumno_sesiones", lang), interactions)
    with col2:
        st.metric(t("alumno_nivel", lang), STUDENT_LEVELS[lang].get(level, level))

    if ctx.get("weak_topics"):
        st.warning(f"{t('alumno_reforzar', lang)} {', '.join(ctx['weak_topics'][:2])}")

    st.divider()

    # Navegación
    if st.button("📝 Ir a Exámenes" if lang == "es" else "📝 Go to Exams",
                 use_container_width=True):
        st.switch_page("pages/4_Examen.py")

    if st.button(t("nueva_sesion", lang), use_container_width=True):
        for key in ["messages_alumno", "orchestrator_alumno"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    # ── CERRAR SESIÓN ─────────────────────────────────────────────────────────
    if st.button("🚪 Cerrar Sesión" if lang == "es" else "🚪 Sign Out",
                 use_container_width=True, type="secondary"):
        logout_user()
        st.switch_page("login.py")

# ── INICIALIZACIÓN DEL AGENTE ─────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error(t("error_api", lang))
    st.stop()

if "orchestrator_alumno" not in st.session_state:
    st.session_state.orchestrator_alumno = CFOOrchestrator(
        api_key=api_key, mode="tutor", sector=sector, lang=lang,
    )
else:
    st.session_state.orchestrator_alumno.update_language(lang, api_key)

if "messages_alumno" not in st.session_state:
    st.session_state.messages_alumno = []

# ── HEADER ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title(t("alumno_titulo", lang))
    st.caption(
        f"{t('alumno_caption', lang)}, **{user['name']}** | "
        f"Sector: **{SECTORS[lang].get(sector, sector)}** | "
        f"{t('alumno_nivel', lang)}: **{STUDENT_LEVELS[lang].get(level, level)}**"
    )
with col_status:
    st.markdown(f"""
    <div style="background:#E8F5E9;border-radius:8px;padding:10px;text-align:center;margin-top:20px">
        <span style="color:#2E7D32;font-weight:bold">{t("agente_activo", lang)}</span>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_chat, tab_progreso, tab_temas = st.tabs([
    t("alumno_tab_chat", lang),
    t("alumno_tab_progreso", lang),
    t("alumno_tab_temas", lang),
])

with tab_chat:
    # Inicio automático con preguntas ALEATORIAS
    if not st.session_state.messages_alumno:
        with st.spinner(t("alumno_iniciando", lang)):
            # Obtener preguntas diagnósticas aleatorias
            diag_questions = get_random_diagnostic_questions(sector=sector, lang=lang, n=2)
            diag_text = "\n".join([f"- {q}" for q in diag_questions]) if diag_questions else ""

            greeting_prompt = get_greeting_prompt("tutor", lang)
            if diag_text:
                greeting_prompt += (
                    f"\n\nUsa estas preguntas diagnósticas aleatorias para evaluar al alumno:\n{diag_text}"
                    if lang == "es" else
                    f"\n\nUse these random diagnostic questions to assess the student:\n{diag_text}"
                )
            result = st.session_state.orchestrator_alumno.run(
                user_message=greeting_prompt,
                session_id=student_id,
                student_id=student_id,
            )
            st.session_state.messages_alumno.append({
                "role": "assistant",
                "content": result["response"],
                "tools": result.get("tools_used", []),
            })

    # Historial de mensajes
    for msg in st.session_state.messages_alumno:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if msg.get("tools") and msg["role"] == "assistant":
                with st.expander(t("herramientas_usadas", lang), expanded=False):
                    st.caption(f"Tools: {', '.join(msg['tools'])}")

    # Input FIJO en la parte inferior
    if prompt := st.chat_input(t("alumno_chat_placeholder", lang)):
        st.session_state.messages_alumno.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(t("analizando", lang)):
                result = st.session_state.orchestrator_alumno.run(
                    user_message=prompt,
                    session_id=student_id,
                    student_id=student_id,
                )
            st.markdown(result["response"])
            if result.get("tools_used"):
                with st.expander(t("herramientas_usadas", lang), expanded=False):
                    st.caption(f"Tools: {', '.join(result['tools_used'])} | ⏱️ {result.get('elapsed_seconds', 0)}s")
        st.session_state.messages_alumno.append({
            "role": "assistant",
            "content": result["response"],
            "tools": result.get("tools_used", []),
        })

with tab_progreso:
    memory2 = StudentMemory()
    ctx2 = memory2.get_context(student_id, n=50)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"📊 {t('alumno_promedio', lang)}", f"{ctx2.get('avg_score', 0):.1f}/10")
    with col2:
        st.metric(t("alumno_sesiones", lang), ctx2.get("total_interactions", 0))
    with col3:
        lv = ctx2.get("level", "basico")
        st.metric(f"🎯 {t('alumno_nivel', lang)}", STUDENT_LEVELS[lang].get(lv, lv))
    with col4:
        weak = len(ctx2.get("weak_topics", []))
        label = "📌 Temas a reforzar" if lang == "es" else "📌 Topics to reinforce"
        st.metric(label, weak)

    if ctx2.get("weak_topics"):
        st.subheader(t("alumno_temas_refuerzo", lang))
        for topic in ctx2["weak_topics"]:
            st.markdown(f"- 🔴 **{topic}** — {t('alumno_temas_reforzar_pedir', lang)}")

    if ctx2.get("evaluations_by_topic"):
        st.subheader(t("alumno_desempeno_tema", lang))
        import pandas as pd
        df = pd.DataFrame(ctx2["evaluations_by_topic"])
        if not df.empty:
            st.dataframe(df, use_container_width=True)

with tab_temas:
    st.subheader(t("alumno_programa_titulo", lang))
    for categoria, subtemas in PROGRAM_TOPICS[lang].items():
        with st.expander(categoria):
            for subtema in subtemas:
                st.markdown(f"  ✓ {subtema}")
            
