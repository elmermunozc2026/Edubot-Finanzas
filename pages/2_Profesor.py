"""
CFO Agent IA - Dashboard del Profesor con Autenticación
"""
import streamlit as st
import sys
import os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import CFOOrchestrator
from memory.database import StudentMemory
from prompts.system_prompts import get_greeting_prompt
from auth.auth_manager import require_auth, logout_user
from i18n.translations import t, SECTORS, RANKING_COLUMNS

st.set_page_config(
    page_title="CFO Agent IA — Profesor",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.kpi-card   { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:12px;
              padding:18px; color:white; text-align:center; margin:4px; }
.kpi-value  { font-size:32px; font-weight:bold; }
.kpi-label  { font-size:13px; opacity:0.85; margin-top:4px; }
.lang-selector { background:#EEF2F7; border-radius:12px; padding:10px; margin-bottom:12px; }
/* Chat fijo */
section[data-testid="stChatInput"] {
    position: fixed !important; bottom: 0 !important;
    left: 0 !important; right: 0 !important;
    width: 100% !important; z-index: 999 !important;
    background: white !important; padding: 12px 20px !important;
    border-top: 2px solid #E0E8F0 !important;
    box-shadow: 0 -4px 12px rgba(31,78,121,0.10) !important;
}
.main .block-container { padding-bottom: 100px !important; }
</style>
""", unsafe_allow_html=True)

# ── AUTENTICACIÓN ─────────────────────────────────────────────────────────────
user = require_auth(allowed_roles=["profesor", "admin"])
lang = st.session_state.get("lang", "es")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="lang-selector">', unsafe_allow_html=True)
    idioma = st.radio(t("language_selector", "es"), ["🇪🇸 Español", "🇺🇸 English"],
                      horizontal=True, key="idioma_profesor",
                      index=0 if lang == "es" else 1)
    st.markdown('</div>', unsafe_allow_html=True)
    new_lang = "en" if "English" in idioma else "es"
    if new_lang != lang:
        for key in ["orchestrator_profesor", "messages_profesor"]:
            st.session_state.pop(key, None)
        st.session_state["lang"] = new_lang
        st.rerun()

    st.image("https://img.icons8.com/fluency/96/teacher.png", width=60)
    st.title("👨‍🏫 CFO Agent IA")
    st.caption("Dashboard Profesor / Teacher Dashboard")
    st.divider()

    st.markdown(f"👤 **{user['name']}**")
    st.caption(f"📧 {user['email']}")
    sector = user.get("sector", "mining")

    st.divider()
    st.subheader(t("profesor_config_clase", lang))
    num_alumnos = st.number_input(t("profesor_num_alumnos", lang), min_value=1, max_value=50, value=20)
    umbral_riesgo = st.slider(t("profesor_umbral_riesgo", lang), 0.0, 10.0, 5.0, 0.5)

    st.divider()
    if st.button(t("profesor_actualizar", lang), use_container_width=True):
        st.rerun()

    st.divider()
    if st.button("🚪 Cerrar Sesión" if lang == "es" else "🚪 Sign Out",
                 use_container_width=True, type="secondary"):
        logout_user()
        st.switch_page("login.py")

# ── INICIALIZACIÓN ────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error(t("error_api", lang))
    st.stop()

memory = StudentMemory()

if "orchestrator_profesor" not in st.session_state:
    st.session_state.orchestrator_profesor = CFOOrchestrator(
        api_key=api_key, mode="professor", sector=sector, lang=lang,
    )
else:
    st.session_state.orchestrator_profesor.update_language(lang, api_key)

if "messages_profesor" not in st.session_state:
    st.session_state.messages_profesor = []

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title(t("profesor_titulo", lang))
st.caption(f"**{user['name']}** | {t('profesor_sector_clase', lang)}: **{SECTORS[lang].get(sector, sector)}**")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
reporte = memory.get_class_report()
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{reporte['total_alumnos']}</div>
    <div class="kpi-label">{t("profesor_kpi_activos", lang)}</div></div>""", unsafe_allow_html=True)
with col2:
    avg = reporte.get('promedio_clase', 0)
    color = "#00AA44" if avg >= 7 else "#FFA500" if avg >= 5 else "#FF4444"
    st.markdown(f"""<div class="kpi-card" style="background:linear-gradient(135deg,{color},{color}99)">
    <div class="kpi-value">{avg:.1f}</div><div class="kpi-label">{t("profesor_kpi_promedio", lang)}</div></div>""",
    unsafe_allow_html=True)
with col3:
    en_riesgo = len(reporte.get('alumnos_en_riesgo', []))
    st.markdown(f"""<div class="kpi-card" style="background:linear-gradient(135deg,#C0392B,#E74C3C)">
    <div class="kpi-value">{en_riesgo}</div><div class="kpi-label">{t("profesor_kpi_riesgo", lang)}</div></div>""",
    unsafe_allow_html=True)
with col4:
    destacados = len(reporte.get('alumnos_destacados', []))
    st.markdown(f"""<div class="kpi-card" style="background:linear-gradient(135deg,#1E8449,#27AE60)">
    <div class="kpi-value">{destacados}</div><div class="kpi-label">{t("profesor_kpi_destacados", lang)}</div></div>""",
    unsafe_allow_html=True)
with col5:
    total = max(reporte['total_alumnos'], 1)
    aprobados = len([r for r in reporte.get('ranking', []) if r['promedio'] >= 6])
    tasa = round((aprobados / total) * 100, 0)
    st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{tasa:.0f}%</div>
    <div class="kpi-label">{t("profesor_kpi_aprobacion", lang)}</div></div>""", unsafe_allow_html=True)

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_ranking, tab_alertas, tab_chat, tab_config = st.tabs([
    t("profesor_tab_ranking", lang), t("profesor_tab_alertas", lang),
    t("profesor_tab_chat", lang), t("profesor_tab_config", lang),
])

with tab_ranking:
    st.subheader(t("profesor_ranking_titulo", lang))
    ranking = reporte.get("ranking", [])
    cols_map = RANKING_COLUMNS[lang]
    if ranking:
        df = pd.DataFrame(ranking)
        df = df.rename(columns={k: v for k, v in cols_map.items() if k in df.columns})
        def color_row(row):
            estado_col = cols_map.get("semaforo", "Estado")
            val = str(row.get(estado_col, ""))
            if "🔴" in val: return ["background-color:#FFF0F0"] * len(row)
            if "🟡" in val: return ["background-color:#FFFBF0"] * len(row)
            if "🟢" in val: return ["background-color:#F0FFF4"] * len(row)
            return [""] * len(row)
        show_cols = [v for k, v in cols_map.items() if v in df.columns]
        st.dataframe(df[show_cols].style.apply(color_row, axis=1), use_container_width=True, height=400)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(t("exportar_csv", lang), data=csv,
                           file_name=f"reporte_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv", use_container_width=True)
    else:
        st.info(t("profesor_sin_datos", lang))

with tab_alertas:
    st.subheader(t("profesor_alertas_titulo", lang))
    alumnos_riesgo = reporte.get("alumnos_en_riesgo", [])
    if alumnos_riesgo:
        st.error(f"⚠️ {len(alumnos_riesgo)} alumno(s) con promedio < {umbral_riesgo}")
        for alumno in alumnos_riesgo:
            with st.expander(f"🔴 {alumno.get('alumno', '')} — {alumno.get('promedio', 0):.1f}/10"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(t("alumno_promedio", lang), f"{alumno.get('promedio', 0):.1f}/10")
                with col_b:
                    temas = alumno.get("temas_debiles", [])
                    if temas:
                        st.write("**Temas a reforzar:**" if lang == "es" else "**Topics to reinforce:**")
                        for tema in temas:
                            st.markdown(f"  - 📌 {tema}")
                st.markdown(f"- {t('profesor_accion1', lang)}")
                st.markdown(f"- {t('profesor_accion2', lang)}")
                st.markdown(f"- {t('profesor_accion3', lang)}")
    else:
        st.success(t("profesor_sin_riesgo", lang))

    st.divider()
    st.subheader(t("profesor_destacados_titulo", lang))
    for alumno in reporte.get("alumnos_destacados", [])[:5]:
        st.success(f"🏆 **{alumno.get('alumno', '')}** — {alumno.get('promedio', 0):.1f}/10")

with tab_chat:
    st.subheader(t("profesor_asistente_titulo", lang))
    st.caption(t("profesor_asistente_caption", lang))

    if not st.session_state.messages_profesor:
        with st.spinner(t("analizando", lang)):
            greeting = get_greeting_prompt("professor", lang)
            result = st.session_state.orchestrator_profesor.run(
                user_message=greeting,
                session_id=f"profesor_{user['email'].replace('@','_')}",
            )
            st.session_state.messages_profesor.append({"role": "assistant", "content": result["response"]})

    for msg in st.session_state.messages_profesor:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👨‍🏫"):
            st.markdown(msg["content"])

    st.markdown(f"**{'💡 Consultas rápidas:' if lang == 'es' else '💡 Quick queries:'}**")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if st.button(t("profesor_quick1", lang), use_container_width=True):
            st.session_state.quick_query_prof = t("profesor_quick1_query", lang)
    with col_s2:
        if st.button(t("profesor_quick2", lang), use_container_width=True):
            st.session_state.quick_query_prof = t("profesor_quick2_query", lang)
    with col_s3:
        if st.button(t("profesor_quick3", lang), use_container_width=True):
            st.session_state.quick_query_prof = t("profesor_quick3_query", lang)

    query = st.session_state.pop("quick_query_prof", None)
    if prompt := (st.chat_input(t("profesor_chat_placeholder", lang)) or query):
        st.session_state.messages_profesor.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👨‍🏫"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(t("analizando", lang)):
                result = st.session_state.orchestrator_profesor.run(
                    user_message=prompt,
                    session_id=f"profesor_{user['email'].replace('@','_')}",
                )
            st.markdown(result["response"])
        st.session_state.messages_profesor.append({"role": "assistant", "content": result["response"]})
        st.rerun()

with tab_config:
    st.subheader(t("profesor_config_titulo", lang))
    col_c1, col_c2 = st.columns(2)
    temas_opciones = {
        "es": ["Ratios Financieros", "Flujo de Caja", "Presupuestos", "CAPEX",
               "Gestión de Riesgos", "Tesorería", "Impuestos", "Control Interno"],
        "en": ["Financial Ratios", "Cash Flow", "Budgets", "CAPEX",
               "Risk Management", "Treasury", "Taxes", "Internal Control"],
    }
    with col_c1:
        st.markdown(f"**{t('profesor_temas_programa', lang)}**")
        st.multiselect(t("profesor_temas_habilitados", lang), temas_opciones[lang], default=temas_opciones[lang][:3])
        st.multiselect(t("profesor_niveles_disponibles", lang),
                       ["basico", "intermedio", "avanzado"] if lang == "es" else ["basic", "intermediate", "advanced"],
                       default=["basico", "intermedio"] if lang == "es" else ["basic", "intermediate"])
    with col_c2:
        st.markdown(f"**{t('profesor_params_eval', lang)}**")
        st.number_input(t("profesor_nota_aprobacion", lang), 0.0, 10.0, 6.0, 0.5)
        st.number_input(t("profesor_preguntas_quiz", lang), 3, 20, 5)
        st.number_input(t("profesor_alerta_inactividad", lang), 1, 14, 3)
    if st.button(t("guardar_config", lang), type="primary", use_container_width=True):
        st.success(t("config_guardada", lang))