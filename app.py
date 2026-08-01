"""
CFO Agent IA - Página Principal (Home) con Soporte Bilingüe
Punto de entrada de la aplicación Streamlit multi-página
"""
import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n.translations import t, SECTORS, MODULES

st.set_page_config(
    page_title="CFO Agent IA",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.hero-title   { font-size:52px; font-weight:900; color:#1F4E79; text-align:center; margin-bottom:8px; }
.hero-sub     { font-size:20px; color:#2E75B6; text-align:center; margin-bottom:32px; font-style:italic; }
.module-card  { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:16px; padding:28px;
                color:white; text-align:center; margin:8px; min-height:180px; }
.module-icon  { font-size:48px; margin-bottom:12px; }
.module-title { font-size:20px; font-weight:bold; margin-bottom:8px; }
.module-desc  { font-size:13px; opacity:0.85; }
.feature-item { background:#F0F4F8; border-radius:10px; padding:14px; margin:6px 0; border-left:4px solid #2E75B6; }
.stat-box     { background:white; border-radius:12px; padding:20px; text-align:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); border-top:4px solid #2E75B6; }
.stat-number  { font-size:36px; font-weight:bold; color:#1F4E79; }
.stat-label   { font-size:13px; color:#666; margin-top:4px; }
.lang-selector{ background:#EEF2F7; border-radius:12px; padding:12px; margin-bottom:16px; }
</style>
""", unsafe_allow_html=True)

# ── SELECTOR DE IDIOMA (SIDEBAR) ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="lang-selector">', unsafe_allow_html=True)
    idioma = st.radio(
        t("language_selector", "es"),
        ["🇪🇸 Español", "🇺🇸 English"],
        horizontal=True,
        key="idioma_global",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Detectar idioma y persistir en session_state
lang = "en" if "English" in idioma else "es"
st.session_state["lang"] = lang

# Si el idioma cambió, limpiar sesiones de agentes para reiniciar con nuevo idioma
if st.session_state.get("last_lang") != lang:
    for key in ["orchestrator_alumno", "orchestrator_profesor", "orchestrator_cfo",
                "messages_alumno", "messages_profesor", "messages_cfo"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["last_lang"] = lang

# ── HERO SECTION ──────────────────────────────────────────────────────────────
st.markdown(f'<div class="hero-title">🏦 {t("app_title", lang)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-sub">{t("app_subtitle", lang)}</div>', unsafe_allow_html=True)

# ── ESTADÍSTICAS ──────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
stats = [
    ("🤖", "3",  t("home_stats_agentes", lang)),
    ("🔧", "20+", t("home_stats_herramientas", lang)),
    ("🏭", "5",  t("home_stats_sectores", lang)),
    ("📚", "8",  t("home_stats_modulos", lang)),
    ("🎓", "20+", t("home_stats_alumnos", lang)),
]
for col, (icon, num, label) in zip([col1, col2, col3, col4, col5], stats):
    with col:
        st.markdown(f"""
        <div class="stat-box">
            <div style="font-size:28px">{icon}</div>
            <div class="stat-number">{num}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── MÓDULOS PRINCIPALES ───────────────────────────────────────────────────────
st.subheader(t("home_modulos_titulo", lang))
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.markdown(f"""
    <div class="module-card">
        <div class="module-icon">🎓</div>
        <div class="module-title">{t("home_mod1_titulo", lang)}</div>
        <div class="module-desc">{t("home_mod1_desc", lang)}</div>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/1_Alumno.py", label=t("home_mod1_link", lang), use_container_width=True)

with col_m2:
    st.markdown(f"""
    <div class="module-card" style="background:linear-gradient(135deg,#1E8449,#27AE60)">
        <div class="module-icon">👨‍🏫</div>
        <div class="module-title">{t("home_mod2_titulo", lang)}</div>
        <div class="module-desc">{t("home_mod2_desc", lang)}</div>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/2_Profesor.py", label=t("home_mod2_link", lang), use_container_width=True)

with col_m3:
    st.markdown(f"""
    <div class="module-card" style="background:linear-gradient(135deg,#7D3C98,#9B59B6)">
        <div class="module-icon">💼</div>
        <div class="module-title">{t("home_mod3_titulo", lang)}</div>
        <div class="module-desc">{t("home_mod3_desc", lang)}</div>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/3_CFO_Asistente.py", label=t("home_mod3_link", lang), use_container_width=True)

st.divider()

# ── CAPACIDADES Y SECTORES ────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(t("home_capacidades_titulo", lang))
    capacidades = {
        "es": [
            ("🧠", "Patrón ReAct", "Ciclo Observar → Razonar → Actuar con Gemini Function Calling"),
            ("💾", "Memoria Persistente", "Historial por alumno y sesiones CFO en SQLite"),
            ("📊", "20+ Herramientas", "Ratios, CAPEX, Tesorería, Riesgos, Impuestos, Control Interno"),
            ("🏭", "Multi-Sector", "Minería, Banca, Retail, Salud y Gobierno"),
            ("🎯", "Adaptativo", "Ajusta dificultad y contenido según el perfil del usuario"),
            ("⚡", "Tiempo Real", "Cálculos financieros instantáneos con datos reales"),
            ("🔔", "Proactivo", "Alertas automáticas sin que el usuario tenga que preguntar"),
            ("📋", "Reporting", "Reportes ejecutivos para Directorio y Matriz"),
        ],
        "en": [
            ("🧠", "ReAct Pattern", "Observe → Reason → Act cycle with Gemini Function Calling"),
            ("💾", "Persistent Memory", "Per-student history and CFO sessions in SQLite"),
            ("📊", "20+ Tools", "Ratios, CAPEX, Treasury, Risks, Taxes, Internal Control"),
            ("🏭", "Multi-Sector", "Mining, Banking, Retail, Health and Government"),
            ("🎯", "Adaptive", "Adjusts difficulty and content based on user profile"),
            ("⚡", "Real Time", "Instant financial calculations with real data"),
            ("🔔", "Proactive", "Automatic alerts without the user having to ask"),
            ("📋", "Reporting", "Executive reports for Board and Parent Company"),
        ],
    }
    for icon, title, desc in capacidades[lang]:
        st.markdown(f"""
        <div class="feature-item">
            <strong>{icon} {title}</strong><br>
            <span style="font-size:13px;color:#555">{desc}</span>
        </div>""", unsafe_allow_html=True)

with col_right:
    st.subheader(t("home_sectores_titulo", lang))
    sectores_desc = {
        "es": {
            "⛏️ Minería y Energía":        "AISC, Cash Cost, Reservas, EBITDA Minero. Marco: MINEM, OSINERGMIN",
            "🏦 Banca y Seguros":           "NIM, NPL, ROE Bancario, Ratio Capital. Marco: SBS Perú, Basilea III",
            "🛒 Retail y Comercio":         "GMV, Ticket Promedio, Rotación Inventario. Marco: INDECOPI, SUNAT",
            "🏥 Salud y Farmacia":          "Costo/Paciente, Ocupación, EBITDA Clínico. Marco: MINSA, DIGEMID",
            "🏛️ Gobierno y Sector Público": "PIM, PIA, Devengado, Ejecución %. Marco: MEF, Contraloría",
        },
        "en": {
            "⛏️ Mining & Energy":       "AISC, Cash Cost, Reserves, Mining EBITDA. Framework: MINEM, OSINERGMIN",
            "🏦 Banking & Insurance":   "NIM, NPL, Banking ROE, Capital Ratio. Framework: SBS Peru, Basel III",
            "🛒 Retail & Commerce":     "GMV, Average Ticket, Inventory Turnover. Framework: INDECOPI, SUNAT",
            "🏥 Health & Pharma":       "Cost/Patient, Occupancy, Clinical EBITDA. Framework: MINSA, DIGEMID",
            "🏛️ Government & Public":   "PIM, PIA, Accrued, Execution %. Framework: MEF, Comptroller",
        },
    }
    for nombre, desc in sectores_desc[lang].items():
        with st.expander(nombre):
            st.caption(desc)

    st.divider()
    st.subheader(t("home_arquitectura_titulo", lang))
    if lang == "es":
        st.markdown("""
        | Componente | Tecnología |
        |---|---|
        | Modelo IA | Gemini 2.0/2.5 Flash |
        | Framework | Google AI Studio |
        | Patrón | ReAct + Function Calling |
        | UI | Streamlit Multi-página |
        | Memoria | SQLite / Firestore |
        | Idiomas | Español / English |
        | Despliegue | Streamlit Cloud / GCP |
        """)
    else:
        st.markdown("""
        | Component | Technology |
        |---|---|
        | AI Model | Gemini 2.0/2.5 Flash |
        | Framework | Google AI Studio |
        | Pattern | ReAct + Function Calling |
        | UI | Streamlit Multi-page |
        | Memory | SQLite / Firestore |
        | Languages | Spanish / English |
        | Deployment | Streamlit Cloud / GCP |
        """)

st.divider()

# ── ROADMAP ───────────────────────────────────────────────────────────────────
st.subheader(t("home_roadmap_titulo", lang))
col_r1, col_r2, col_r3 = st.columns(3)

roadmap = {
    "es": [
        ("✅ Fase 1 — Fundamentos (Semanas 1-4)",
         "- Orchestrator con Function Calling\n- Memoria persistente SQLite\n- 20+ herramientas financieras\n- Migración a Gemini 2.0 Flash"),
        ("🔄 Fase 2 — Módulos Avanzados (Semanas 5-8)",
         "- Dashboard del profesor completo\n- Módulo CFO Asistente ejecutivo\n- Alertas proactivas automáticas\n- Exportación de reportes PDF"),
        ("🚀 Fase 3 — Expansión (Meses 3-6)",
         "- Módulos bancario y retail\n- Expansión a salud y gobierno\n- Mercados internacionales\n- API pública para integraciones"),
    ],
    "en": [
        ("✅ Phase 1 — Foundations (Weeks 1-4)",
         "- Orchestrator with Function Calling\n- Persistent SQLite memory\n- 20+ financial tools\n- Migration to Gemini 2.0 Flash"),
        ("🔄 Phase 2 — Advanced Modules (Weeks 5-8)",
         "- Complete teacher dashboard\n- CFO Executive Assistant module\n- Automatic proactive alerts\n- PDF report export"),
        ("🚀 Phase 3 — Expansion (Months 3-6)",
         "- Banking and retail modules\n- Expansion to health and government\n- International markets\n- Public API for integrations"),
    ],
}

for col, (titulo, contenido) in zip([col_r1, col_r2, col_r3], roadmap[lang]):
    with col:
        st.markdown(f"**{titulo}**\n{contenido}")

st.divider()
footer = {
    "es": "CFO Agent IA © 2026 | Desarrollado con Google Gemini + Streamlit | Multi-Sector | 🇪🇸 Español / 🇺🇸 English",
    "en": "CFO Agent IA © 2026 | Built with Google Gemini + Streamlit | Multi-Sector | 🇪🇸 Spanish / 🇺🇸 English",
}
st.caption(footer[lang])