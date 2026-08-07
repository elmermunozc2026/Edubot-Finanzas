"""
CFO Agent IA - Módulo Asistente Ejecutivo CFO con Autenticación
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import CFOOrchestrator
from prompts.system_prompts import get_greeting_prompt
from auth.auth_manager import require_auth, logout_user
from i18n.translations import t, SECTORS, MODULES, AUDIT_PROCESSES, RISK_CATEGORIES, TAX_REGIMES

st.set_page_config(
    page_title="CFO Agent IA — Asistente Ejecutivo",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.lang-selector{ background:#EEF2F7; border-radius:12px; padding:10px; margin-bottom:12px; }
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
user = require_auth(allowed_roles=["cfo", "admin"])
lang = st.session_state.get("lang", "es")
sector = user.get("sector", "mining")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="lang-selector">', unsafe_allow_html=True)
    idioma = st.radio(t("language_selector", "es"), ["🇪🇸 Español", "🇺🇸 English"],
                      horizontal=True, key="idioma_cfo",
                      index=0 if lang == "es" else 1)
    st.markdown('</div>', unsafe_allow_html=True)
    new_lang = "en" if "English" in idioma else "es"
    if new_lang != lang:
        for key in ["orchestrator_cfo", "messages_cfo"]:
            st.session_state.pop(key, None)
        st.session_state["lang"] = new_lang
        st.rerun()

    st.image("https://img.icons8.com/fluency/96/businessman.png", width=60)
    st.title("💼 CFO Agent IA")
    st.caption("Asistente Ejecutivo / Executive Assistant")
    st.divider()

    st.markdown(f"👤 **{user['name']}**")
    st.caption(f"📧 {user['email']}")
    st.caption(f"🏭 {SECTORS[lang].get(sector, sector)}")
    st.divider()

    st.subheader(t("cfo_modulos", lang))
    modulos_lista = MODULES[lang]
    modulo_activo = st.radio("", modulos_lista, label_visibility="collapsed")

    st.divider()
    if st.button(t("cfo_nueva_sesion", lang), use_container_width=True):
        for key in ["messages_cfo", "orchestrator_cfo"]:
            st.session_state.pop(key, None)
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

# ── MODELO: usar el disponible en la cuenta ───────────────────────────────────
MODEL_NAME = "models/gemini-3.6-flash"

if "orchestrator_cfo" not in st.session_state:
    st.session_state.orchestrator_cfo = CFOOrchestrator(
        api_key=api_key, mode="cfo", sector=sector, lang=lang,
        model_name=MODEL_NAME,
    )
else:
    st.session_state.orchestrator_cfo.update_language(lang, api_key, MODEL_NAME)

if "messages_cfo" not in st.session_state:
    st.session_state.messages_cfo = []

session_id = f"cfo_{user['email'].replace('@','_').replace('.','_')}"

# ── HEADER ────────────────────────────────────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.title(t("cfo_titulo", lang))
    st.caption(f"**{user['name']}** | {t('cfo_sector', lang)}: **{SECTORS[lang].get(sector, sector)}**")
with col_h2:
    st.markdown(f"""<div style="background:#E8F5E9;border-radius:8px;padding:10px;text-align:center;margin-top:20px">
    <span style="color:#2E7D32;font-weight:bold">{t("agente_activo", lang)}</span></div>""",
    unsafe_allow_html=True)
with col_h3:
    st.markdown(f"""<div style="background:#EEF2F7;border-radius:8px;padding:10px;text-align:center;margin-top:20px">
    <span style="color:#1F4E79;font-size:12px">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span></div>""",
    unsafe_allow_html=True)

st.divider()

def run_agent(query: str, spinner_key: str = "analizando") -> str:
    with st.spinner(t(spinner_key, lang)):
        result = st.session_state.orchestrator_cfo.run(user_message=query, session_id=session_id)
    st.markdown(result["response"])
    if result.get("tools_used"):
        with st.expander(t("herramientas_usadas", lang), expanded=False):
            st.caption(f"Tools: {', '.join(result['tools_used'])} | ⏱️ {result.get('elapsed_seconds',0)}s")
    return result["response"]

mod_idx = modulos_lista.index(modulo_activo) if modulo_activo in modulos_lista else 0

# ── 0: CHAT EJECUTIVO ─────────────────────────────────────────────────────────
if mod_idx == 0:
    st.subheader(t("cfo_chat_titulo", lang))
    if not st.session_state.messages_cfo:
        with st.spinner(t("cfo_iniciando", lang)):
            greeting = get_greeting_prompt("cfo", lang)
            result = st.session_state.orchestrator_cfo.run(user_message=greeting, session_id=session_id)
            st.session_state.messages_cfo.append({"role":"assistant","content":result["response"],"tools":result.get("tools_used",[])})

    for msg in st.session_state.messages_cfo:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"]=="assistant" else "💼"):
            st.markdown(msg["content"])
            if msg.get("tools") and msg["role"]=="assistant":
                with st.expander(t("herramientas_usadas", lang), expanded=False):
                    st.caption(f"Tools: {', '.join(msg['tools'])}")

    st.markdown(f"**⚡ {'Consultas rápidas:' if lang=='es' else 'Quick queries:'}**")
    cols = st.columns(4)
    quick_queries = [
        (t("cfo_quick_ratios", lang), f"Calcula ratios: AC=2.5M, PC=1.2M, ventas=8M, UN=1.2M, patrimonio=5M, EBITDA=2M, deuda=3M. Sector {sector}." if lang=="es" else f"Calculate ratios: CA=2.5M, CL=1.2M, sales=8M, NI=1.2M, equity=5M, EBITDA=2M, debt=3M. Sector {sector}."),
        (t("cfo_quick_caja", lang), "Posicion de caja: BCP=850K, BBVA=420K, Scotiabank=180K, cobros=300K, pagos=450K, lineas=2M." if lang=="es" else "Cash position: BCP=850K, BBVA=420K, Scotiabank=180K, collections=300K, payments=450K, lines=2M."),
        (t("cfo_quick_riesgos", lang), f"Matriz de riesgos sector {sector}." if lang=="es" else f"Risk matrix for {sector} sector."),
        (t("cfo_quick_sunat", lang), f"Obligaciones tributarias mes {datetime.now().month}/{datetime.now().year}." if lang=="es" else f"Tax obligations month {datetime.now().month}/{datetime.now().year}."),
    ]
    for i, (label, query) in enumerate(quick_queries):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"quick_{i}"):
                st.session_state.quick_cfo_query = query

    query = st.session_state.pop("quick_cfo_query", None)
    if prompt := (st.chat_input(t("cfo_chat_placeholder", lang)) or query):
        st.session_state.messages_cfo.append({"role":"user","content":prompt})
        with st.chat_message("user", avatar="💼"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            resp = run_agent(prompt)
        st.session_state.messages_cfo.append({"role":"assistant","content":resp,"tools":[]})
        st.rerun()

# ── 1: ANÁLISIS FINANCIERO ────────────────────────────────────────────────────
elif mod_idx == 1:
    st.subheader(t("cfo_analisis_titulo", lang))
    with st.form("form_ratios"):
        st.markdown(f"**{t('cfo_balance_titulo', lang)}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            ac = st.number_input("Activo Corriente/Current Assets (S/)", value=2_500_000.0, step=100_000.0)
            at = st.number_input("Activo Total/Total Assets (S/)", value=15_000_000.0, step=100_000.0)
        with c2:
            pc = st.number_input("Pasivo Corriente/Current Liabilities (S/)", value=1_200_000.0, step=100_000.0)
            pt = st.number_input("Pasivo Total/Total Liabilities (S/)", value=6_000_000.0, step=100_000.0)
        with c3:
            pat = st.number_input("Patrimonio/Equity (S/)", value=9_000_000.0, step=100_000.0)
            inv = st.number_input("Inventario/Inventory (S/)", value=400_000.0, step=50_000.0)
        st.markdown(f"**{t('cfo_eerr_titulo', lang)}**")
        c4, c5, c6 = st.columns(3)
        with c4:
            ven = st.number_input("Ventas/Sales (S/)", value=8_000_000.0, step=100_000.0)
        with c5:
            uop = st.number_input("Utilidad Operativa/EBIT (S/)", value=1_600_000.0, step=100_000.0)
            un  = st.number_input("Utilidad Neta/Net Income (S/)", value=1_200_000.0, step=100_000.0)
        with c6:
            ebitda = st.number_input("EBITDA (S/)", value=2_000_000.0, step=100_000.0)
            deuda  = st.number_input("Deuda Financiera/Financial Debt (S/)", value=3_000_000.0, step=100_000.0)
        if st.form_submit_button(t("cfo_calcular_ratios", lang), type="primary", use_container_width=True):
            q = (f"Calcula ratios: AC={ac},PC={pc},AT={at},PT={pt},patrimonio={pat},UN={un},UOP={uop},ventas={ven},inv={inv},EBITDA={ebitda},deuda={deuda}. Sector:{sector}."
                 if lang == "es" else
                 f"Calculate ratios: CA={ac},CL={pc},TA={at},TL={pt},equity={pat},NI={un},EBIT={uop},sales={ven},inv={inv},EBITDA={ebitda},debt={deuda}. Sector:{sector}.")
            st.markdown(t("cfo_analisis_ejecutivo", lang))
            run_agent(q, "cfo_calculando_ratios")

# ── 2: PLANEAMIENTO ───────────────────────────────────────────────────────────
elif mod_idx == 2:
    st.subheader(t("cfo_planeamiento_titulo", lang))
    tab_b, tab_f, tab_c = st.tabs([t("cfo_tab_presupuesto", lang), t("cfo_tab_forecast", lang), t("cfo_tab_capex", lang)])
    with tab_b:
        with st.form("form_budget"):
            c1, c2 = st.columns(2)
            with c1:
                year  = st.number_input("Año/Year:", value=2027, min_value=2024, max_value=2035)
                rev   = st.number_input("Ingresos base/Base Revenue (S/):", value=8_000_000.0, step=500_000.0)
                growth = st.slider("Crecimiento/Growth:", -0.20, 0.50, 0.08, 0.01, format="%.0f%%")
            with c2:
                cost_r = st.slider("Ratio costos/Cost ratio:", 0.30, 0.80, 0.60, 0.01, format="%.0f%%")
                opex_r = st.slider("Ratio OPEX:", 0.05, 0.40, 0.20, 0.01, format="%.0f%%")
            if st.form_submit_button(t("cfo_construir_presupuesto", lang), type="primary", use_container_width=True):
                q = (f"Construye presupuesto {year}: ingresos={rev}, crecimiento={growth:.2f}, costos={cost_r:.2f}, opex={opex_r:.2f}, sector={sector}."
                     if lang == "es" else
                     f"Build budget {year}: revenue={rev}, growth={growth:.2f}, costs={cost_r:.2f}, opex={opex_r:.2f}, sector={sector}.")
                run_agent(q, "cfo_construyendo_presupuesto")
    with tab_f:
        with st.form("form_forecast"):
            c1, c2 = st.columns(2)
            with c1:
                ytd    = st.number_input("Ingresos YTD (S/):", value=4_200_000.0, step=100_000.0)
                months = st.number_input("Meses/Months:", value=6, min_value=1, max_value=12)
            with c2:
                scenario = st.selectbox("Escenario/Scenario:", ["base", "optimista", "pesimista"])
                comm     = st.slider("Commodity change:", -0.30, 0.30, 0.0, 0.01, format="%.0f%%")
            if st.form_submit_button(t("cfo_proyectar_forecast", lang), type="primary", use_container_width=True):
                q = (f"Forecast: YTD={ytd}, meses={months}, escenario={scenario}, commodity={comm:.2f}. Sector:{sector}."
                     if lang == "es" else
                     f"Forecast: YTD={ytd}, months={months}, scenario={scenario}, commodity={comm:.2f}. Sector:{sector}.")
                run_agent(q, "cfo_proyectando")
    with tab_c:
        with st.form("form_capex"):
            proj = st.text_input(t("cfo_nombre_proyecto", lang), value="Expansion Planta" if lang == "es" else "Plant Expansion")
            c1, c2 = st.columns(2)
            with c1:
                inv_ini = st.number_input("Inversion/Investment (S/):", value=5_000_000.0, step=100_000.0)
                wacc    = st.slider("WACC:", 0.05, 0.25, 0.12, 0.01, format="%.0f%%")
                vida    = st.number_input("Vida util/Life (anos/years):", value=5, min_value=1, max_value=20)
            with c2:
                st.markdown(t("cfo_flujos_proyectados", lang))
                flujos = [st.number_input(f"{'Ano' if lang == 'es' else 'Year'} {i}:", value=1_500_000.0, step=100_000.0, key=f"fc_{i}") for i in range(1, int(vida) + 1)]
            if st.form_submit_button(t("cfo_evaluar_capex", lang), type="primary", use_container_width=True):
                q = (f"Evalua CAPEX '{proj}': inversion={inv_ini}, flujos={flujos}, WACC={wacc:.2f}, vida={vida} anos."
                     if lang == "es" else
                     f"Evaluate CAPEX '{proj}': investment={inv_ini}, cash flows={flujos}, WACC={wacc:.2f}, life={vida} years.")
                run_agent(q, "cfo_evaluando")

# ── 3: TESORERÍA ──────────────────────────────────────────────────────────────
elif mod_idx == 3:
    st.subheader(t("cfo_tesoreria_titulo", lang))
    tab_ca, tab_ba, tab_wc = st.tabs([t("cfo_tab_caja", lang), t("cfo_tab_bancos", lang), t("cfo_tab_wc", lang)])
    with tab_ca:
        with st.form("form_caja"):
            st.markdown(f"**{t('cfo_saldos_banco', lang)}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                bcp  = st.number_input("BCP (S/):", value=850_000.0, step=10_000.0)
                bbva = st.number_input("BBVA (S/):", value=420_000.0, step=10_000.0)
            with c2:
                scot  = st.number_input("Scotiabank (S/):", value=180_000.0, step=10_000.0)
                inter = st.number_input("Interbank (S/):", value=95_000.0, step=10_000.0)
            with c3:
                cobros = st.number_input("Cobros/Collections (S/):", value=300_000.0, step=10_000.0)
                pagos  = st.number_input("Pagos/Payments (S/):", value=450_000.0, step=10_000.0)
                lineas = st.number_input("Lineas/Lines (S/):", value=2_000_000.0, step=100_000.0)
            if st.form_submit_button(t("cfo_calcular_posicion", lang), type="primary", use_container_width=True):
                saldos = {"BCP": bcp, "BBVA": bbva, "Scotiabank": scot, "Interbank": inter}
                q = (f"Posicion de caja: saldos={json.dumps(saldos)}, cobros={cobros}, pagos={pagos}, lineas={lineas}."
                     if lang == "es" else
                     f"Cash position: balances={json.dumps(saldos)}, collections={cobros}, payments={pagos}, lines={lineas}.")
                run_agent(q, "cfo_calculando_caja")
    with tab_ba:
        with st.form("form_banco"):
            c1, c2 = st.columns(2)
            with c1:
                banco = st.selectbox("Banco/Bank:", ["BCP", "BBVA", "Scotiabank", "Interbank", "Banco de la Nacion"])
                tipo_opts = {
                    "es": ["Linea revolvente", "Prestamo a plazo", "Carta fianza", "Factoring", "Leasing"],
                    "en": ["Revolving line", "Term loan", "Bank guarantee", "Factoring", "Leasing"],
                }
                tipo  = st.selectbox("Tipo/Type:", tipo_opts[lang])
                monto = st.number_input("Monto/Amount (S/):", value=3_000_000.0, step=100_000.0)
            with c2:
                usado = st.number_input("Utilizado/Used (S/):", value=1_800_000.0, step=100_000.0)
                tasa  = st.number_input("Tasa/Rate (%):", value=8.5, step=0.1) / 100
                venc  = st.date_input("Vencimiento/Maturity:")
            if st.form_submit_button(t("cfo_analizar_linea", lang), type="primary", use_container_width=True):
                q = (f"Linea bancaria {banco}: tipo={tipo}, monto={monto}, usado={usado}, tasa={tasa:.4f}, vencimiento={venc}."
                     if lang == "es" else
                     f"Bank line {banco}: type={tipo}, amount={monto}, used={usado}, rate={tasa:.4f}, maturity={venc}.")
                run_agent(q, "cfo_analizando_linea")
    with tab_wc:
        with st.form("form_wc"):
            c1, c2 = st.columns(2)
            with c1:
                cxc    = st.number_input("CxC/AR (S/):", value=1_200_000.0, step=50_000.0)
                inv_wc = st.number_input("Inventario/Inventory (S/):", value=600_000.0, step=50_000.0)
                cxp    = st.number_input("CxP/AP (S/):", value=800_000.0, step=50_000.0)
            with c2:
                vd = st.number_input("Ventas diarias/Daily sales (S/):", value=22_000.0, step=1_000.0)
                cd = st.number_input("Costo diario/Daily cost (S/):", value=13_000.0, step=1_000.0)
            if st.form_submit_button(t("cfo_optimizar_wc", lang), type="primary", use_container_width=True):
                q = (f"Capital de trabajo: CxC={cxc}, inv={inv_wc}, CxP={cxp}, ventas_dia={vd}, costo_dia={cd}."
                     if lang == "es" else
                     f"Working capital: AR={cxc}, inv={inv_wc}, AP={cxp}, daily_sales={vd}, daily_cost={cd}.")
                run_agent(q, "cfo_analizando_wc")

# ── 4: RIESGOS ────────────────────────────────────────────────────────────────
elif mod_idx == 4:
    st.subheader(t("cfo_riesgos_titulo", lang))
    tab_mx, tab_ri, tab_vr = st.tabs([t("cfo_tab_matriz", lang), t("cfo_tab_riesgo", lang), t("cfo_tab_var", lang)])
    with tab_mx:
        if st.button(t("cfo_cargar_matriz", lang), type="primary", use_container_width=True):
            run_agent(f"Matriz de riesgos sector {sector}." if lang == "es" else f"Risk matrix for {sector} sector.", "cfo_cargando_matriz")
    with tab_ri:
        with st.form("form_riesgo"):
            nombre_r = st.text_input(t("cfo_nombre_riesgo", lang), value="Caida precio cobre" if lang == "es" else "Copper price drop")
            c1, c2 = st.columns(2)
            with c1:
                cat  = st.selectbox(t("cfo_categoria", lang), RISK_CATEGORIES[lang])
                prob = st.slider(t("cfo_probabilidad", lang), 0.0, 1.0, 0.35, 0.05, format="%.0f%%")
            with c2:
                imp = st.slider(t("cfo_impacto", lang), 0.0, 1.0, 0.30, 0.05, format="%.0f%%")
                ing = st.number_input(t("cfo_ingresos_anuales", lang), value=8_000_000.0, step=500_000.0)
            if st.form_submit_button(t("cfo_evaluar_riesgo_btn", lang), type="primary", use_container_width=True):
                q = (f"Evalua riesgo '{nombre_r}': cat={cat}, prob={prob}, impacto={imp}, ingresos={ing}."
                     if lang == "es" else
                     f"Assess risk '{nombre_r}': cat={cat}, prob={prob}, impact={imp}, revenue={ing}.")
                run_agent(q, "cfo_calculando")
    with tab_vr:
        with st.form("form_var"):
            c1, c2 = st.columns(2)
            with c1:
                port = st.number_input("Portafolio/Portfolio (S/):", value=5_000_000.0, step=100_000.0)
                vol  = st.slider("Volatilidad/Volatility:", 0.001, 0.05, 0.015, 0.001, format="%.1f%%")
            with c2:
                conf = st.selectbox("Confianza/Confidence:", [0.90, 0.95, 0.99], index=2, format_func=lambda x: f"{x*100:.0f}%")
                hor  = st.number_input("Horizonte/Horizon (dias/days):", value=1, min_value=1, max_value=30)
            if st.form_submit_button(t("cfo_calcular_var", lang), type="primary", use_container_width=True):
                q = (f"VaR: portafolio={port}, volatilidad={vol}, confianza={conf}, horizonte={hor} dias."
                     if lang == "es" else
                     f"VaR: portfolio={port}, volatility={vol}, confidence={conf}, horizon={hor} days.")
                run_agent(q, "cfo_calculando")

# ── 5: IMPUESTOS ──────────────────────────────────────────────────────────────
elif mod_idx == 5:
    st.subheader(t("cfo_impuestos_titulo", lang))
    tab_ir, tab_igv, tab_cal = st.tabs([t("cfo_tab_ir", lang), t("cfo_tab_igv", lang), t("cfo_tab_calendario", lang)])
    with tab_ir:
        with st.form("form_ir"):
            c1, c2 = st.columns(2)
            with c1:
                util   = st.number_input("Utilidad/Pre-tax income (S/):", value=1_500_000.0, step=50_000.0)
                adic   = st.number_input("Adiciones/Additions (S/):", value=120_000.0, step=10_000.0)
                dedu   = st.number_input("Deducciones/Deductions (S/):", value=80_000.0, step=10_000.0)
            with c2:
                pagos_c = st.number_input("Pagos a cuenta/Advance payments (S/):", value=350_000.0, step=10_000.0)
                reg     = st.selectbox("Regimen/Regime:", list(TAX_REGIMES[lang].keys()), format_func=lambda x: TAX_REGIMES[lang][x])
            if st.form_submit_button(t("cfo_calcular_ir", lang), type="primary", use_container_width=True):
                q = (f"IR: utilidad={util}, adiciones={adic}, deducciones={dedu}, pagos_cuenta={pagos_c}, regimen={reg}."
                     if lang == "es" else
                     f"Income tax: income={util}, additions={adic}, deductions={dedu}, advance={pagos_c}, regime={reg}.")
                run_agent(q, "cfo_calculando_ir")
    with tab_igv:
        with st.form("form_igv"):
            c1, c2 = st.columns(2)
            with c1:
                igv_v = st.number_input("IGV ventas/Sales VAT (S/):", value=288_000.0, step=10_000.0)
                igv_c = st.number_input("IGV compras/Purchase VAT (S/):", value=180_000.0, step=10_000.0)
            with c2:
                saldo_ant = st.number_input("Saldo anterior/Prior credit (S/):", value=0.0, step=10_000.0)
            if st.form_submit_button(t("cfo_calcular_igv", lang), type="primary", use_container_width=True):
                q = (f"IGV: debito={igv_v}, credito={igv_c}, saldo_anterior={saldo_ant}."
                     if lang == "es" else
                     f"VAT: debit={igv_v}, credit={igv_c}, prior_balance={saldo_ant}.")
                run_agent(q, "cfo_calculando_igv")
    with tab_cal:
        mes_sel = st.selectbox("Mes/Month:", list(range(1, 13)), index=datetime.now().month - 1,
                               format_func=lambda m: datetime(2026, m, 1).strftime("%B"))
        if st.button(t("cfo_ver_calendario", lang), type="primary", use_container_width=True):
            q = (f"Calendario tributario SUNAT mes {mes_sel}/2026, sector {sector}."
                 if lang == "es" else
                 f"SUNAT tax calendar month {mes_sel}/2026, sector {sector}.")
            run_agent(q, "cfo_cargando_calendario")

# ── 6: CONTROL INTERNO ────────────────────────────────────────────────────────
elif mod_idx == 6:
    st.subheader(t("cfo_control_titulo", lang))
    proceso = st.selectbox(t("cfo_proceso_auditar", lang), list(AUDIT_PROCESSES[lang].keys()),
                           format_func=lambda x: AUDIT_PROCESSES[lang][x])
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t("cfo_evaluar_controles", lang), type="primary", use_container_width=True):
            q = (f"Controles internos proceso {proceso}, sector {sector}. Identifica brechas y mejoras."
                 if lang == "es" else
                 f"Internal controls for {proceso} process, sector {sector}. Identify gaps and improvements.")
            run_agent(q, "cfo_evaluando_controles")
    with c2:
        mes_reg = st.number_input(t("cfo_mes_regulatorio", lang), value=datetime.now().month, min_value=1, max_value=12)
        if st.button(t("cfo_ver_obligaciones", lang), use_container_width=True):
            q = (f"Obligaciones regulatorias mes {mes_reg}, sector {sector}, Peru."
                 if lang == "es" else
                 f"Regulatory obligations month {mes_reg}, sector {sector}, Peru.")
            run_agent(q, "cfo_cargando_obligaciones")

# ── 7: REPORTING ──────────────────────────────────────────────────────────────
elif mod_idx == 7:
    st.subheader(t("cfo_reporting_titulo", lang))
    st.caption(t("cfo_reporting_caption", lang))
    with st.form("form_reporting"):
        periodo = st.text_input(t("cfo_periodo_reporte", lang), value="Q2 2026")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(t("cfo_kpis_clave", lang))
            kpi1 = st.text_input("KPI 1:", value="Ingresos: S/ 4.2M (+8% vs presupuesto)" if lang == "es" else "Revenue: S/ 4.2M (+8% vs budget)")
            kpi2 = st.text_input("KPI 2:", value="EBITDA: S/ 1.1M (Margen 26%)" if lang == "es" else "EBITDA: S/ 1.1M (Margin 26%)")
            kpi3 = st.text_input("KPI 3:", value="Liquidez corriente: 2.1x" if lang == "es" else "Current ratio: 2.1x")
        with c2:
            st.markdown(t("cfo_logros_periodo", lang))
            logro1 = st.text_input("1:", value="Reduccion costos 5%" if lang == "es" else "5% cost reduction")
            logro2 = st.text_input("2:", value="Renovacion linea BCP S/ 3M" if lang == "es" else "BCP line renewal S/ 3M")
            logro3 = st.text_input("3:", value="Cero observaciones auditoria" if lang == "es" else "Zero audit findings")
        if st.form_submit_button(t("cfo_generar_reporte", lang), type="primary", use_container_width=True):
            q = (f"Reporte ejecutivo {periodo}: KPIs={kpi1},{kpi2},{kpi3}. Logros={logro1},{logro2},{logro3}. Sector {sector}."
                 if lang == "es" else
                 f"Executive report {periodo}: KPIs={kpi1},{kpi2},{kpi3}. Achievements={logro1},{logro2},{logro3}. Sector {sector}.")
            st.markdown(t("cfo_reporte_titulo", lang))
            resp = run_agent(q, "cfo_generando_reporte")
            st.download_button(t("descargar_reporte", lang), data=resp,
                               file_name=f"report_{periodo.replace(' ', '_')}.txt", mime="text/plain")