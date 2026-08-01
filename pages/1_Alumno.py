"""
CFO Agent IA - Página del Alumno con Soporte Bilingüe
Interfaz de chat educativo con historial, nivel y progreso visual
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import CFOOrchestrator
from memory.database import StudentMemory
from prompts.system_prompts import get_greeting_prompt
from i18n.translations import t, SECTORS, STUDENT_LEVELS, PROGRAM_TOPICS

st.set_page_config(
    page_title="CFO Agent IA — Alumno / Student",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.metric-card  { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:12px;
                padding:16px; color:white; text-align:center; margin:4px; }
.metric-value { font-size:28px; font-weight:bold; }
.metric-label { font-size:12px; opacity:0.85; }
.lang-selector{ background:#EEF2F7; border-radius:12px; padding:10px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

# ── SELECTOR DE IDIOMA ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="lang-selector">', unsafe_allow_html=True)
    idioma = st.radio(
        t("language_selector", "es"),
        ["🇪🇸 Español", "🇺🇸 English"],
        horizontal=True,
        key="idioma_alumno",
        index=0 if st.session_state.get("lang", "es") == "es" else 1,
    )
    st.markdown('</div>', unsafe_allow_html=True)

lang = "en" if "English" in idioma else "es"

# Si el idioma cambió, limpiar sesión del agente
if st.session_state.get("lang_alumno") != lang:
    for key in ["orchestrator_alumno", "messages_alumno"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["lang_alumno"] = lang
st.session_state["lang"] = lang

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=60)
    st.title("🎓 CFO Agent IA")
    st.caption("Módulo Educativo / Educational Module")
    st.divider()

    nombre = st.text_input(
        t("alumno_nombre", lang),
        placeholder=t("alumno_nombre_placeholder", lang),
        key="nombre_alumno"
    )
    student_id = nombre.lower().replace(" ", "_") if nombre else "alumno_demo"

    sector = st.selectbox(
        t("alumno_sector", lang),
        list(SECTORS[lang].keys()),
        format_func=lambda x: SECTORS[lang][x],
    )

    st.divider()

    # Progreso del alumno
    if nombre:
        memory = StudentMemory()
        ctx = memory.get_context(student_id, n=20)
        avg = ctx.get("avg_score", 0)
        level = ctx.get("level", "basico")
        interactions = ctx.get("total_interactions", 0)

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg:.1f}/10</div>
            <div class="metric-label">{t("alumno_promedio", lang)}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(t("alumno_sesiones", lang), interactions)
        with col2:
            st.metric(t("alumno_nivel", lang), STUDENT_LEVELS[lang].get(level, level))

        if ctx.get("weak_topics"):
            st.warning(f"{t('alumno_reforzar', lang)} {', '.join(ctx['weak_topics'][:2])}")

    st.divider()
    if st.button(t("nueva_sesion", lang), use_container_width=True):
        for key in ["messages_alumno", "orchestrator_alumno"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ── INICIALIZACIÓN DEL AGENTE ─────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error(t("error_api", lang))
    st.stop()

# Crear o actualizar el orchestrator con el idioma correcto
if "orchestrator_alumno" not in st.session_state:
    st.session_state.orchestrator_alumno = CFOOrchestrator(
        api_key=api_key,
        mode="tutor",
        sector=sector,
        lang=lang,
    )
else:
    # Actualizar idioma si cambió
    st.session_state.orchestrator_alumno.update_language(lang, api_key)

if "messages_alumno" not in st.session_state:
    st.session_state.messages_alumno = []

# ── HEADER ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title(t("alumno_titulo", lang))
    if nombre:
        memory = StudentMemory()
        ctx = memory.get_context(student_id, n=20)
        level = ctx.get("level", "basico")
        st.caption(
            f"{t('alumno_caption', lang)}, **{nombre}** | "
            f"Sector: **{SECTORS[lang][sector]}** | "
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
    # Inicio automático de sesión
    if not st.session_state.messages_alumno and nombre:
        with st.spinner(t("alumno_iniciando", lang)):
            greeting_prompt = get_greeting_prompt("tutor", lang)
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

    # Input del alumno
    if not nombre:
        st.info(t("alumno_ingresa_nombre", lang))
    else:
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
    if nombre:
        memory = StudentMemory()
        ctx = memory.get_context(student_id, n=50)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"📊 {t('alumno_promedio', lang)}", f"{ctx.get('avg_score', 0):.1f}/10")
        with col2:
            st.metric(t("alumno_sesiones", lang), ctx.get("total_interactions", 0))
        with col3:
            level = ctx.get("level", "basico")
            st.metric(f"🎯 {t('alumno_nivel', lang)}", STUDENT_LEVELS[lang].get(level, level))
        with col4:
            weak = len(ctx.get("weak_topics", []))
            label = "📌 Temas a reforzar" if lang == "es" else "📌 Topics to reinforce"
            st.metric(label, weak)

        if ctx.get("weak_topics"):
            st.subheader(t("alumno_temas_refuerzo", lang))
            for topic in ctx["weak_topics"]:
                st.markdown(f"- 🔴 **{topic}** — {t('alumno_temas_reforzar_pedir', lang)}")

        if ctx.get("evaluations_by_topic"):
            st.subheader(t("alumno_desempeno_tema", lang))
            import pandas as pd
            df = pd.DataFrame(ctx["evaluations_by_topic"])
            if not df.empty:
                st.dataframe(df, use_container_width=True)
    else:
        st.info(t("alumno_ingresa_nombre_progreso", lang))

with tab_temas:
    st.subheader(t("alumno_programa_titulo", lang))
    topics = PROGRAM_TOPICS[lang]
    for categoria, subtemas in topics.items():
        with st.expander(categoria):
            for subtema in subtemas:
                st.markdown(f"  ✓ {subtema}")