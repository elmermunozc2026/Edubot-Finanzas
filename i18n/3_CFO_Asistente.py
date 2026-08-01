"""
CFO Agent IA - Módulo Asistente Ejecutivo CFO con Soporte Bilingüe
Panel para el Director de Finanzas o Gerente General
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import CFOOrchestrator
from prompts.system_prompts import get_greeting_prompt
from i18n.translations import t, SECTORS, MODULES, AUDIT_PROCESSES, RISK_CATEGORIES, TAX_REGIMES

st.set_page_config(
    page_title="CFO Agent IA — Asistente Ejecutivo / Executive Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.exec-card    { background:linear-gradient(135deg,#1F4E79,#2E75B6); border-radius:12px;
                padding:20px; color:white; margin:6px 0; }
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
        key="idioma_cfo",
        index=0 if st.session_state.get("lang", "es") == "es" else 1,
    )
    st.markdown('</div>', unsafe_allow_html=True)

lang = "en" if "English" in idioma else "es"

if st.session_state.get("lang_cfo") != lang:
    for key in ["orchestrator_cfo", "messages_cfo"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["lang_cfo"] = lang
st.session_state["lang"] = lang

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/businessman.png", width=60)
    st.title("💼 CFO Agent IA")
    st.caption("Asistente Ejecutivo / Executive Assistant")
    st.divider()

    nombre_cfo = st.text_input(t("cfo_nombre", lang), value="CFO Ejecutivo")
    empresa    = st.text_input(t("cfo_empresa", lang), value="Compañía Minera Los Andes SAC")
    sector     = st.selectbox(
        t("cfo_sector", lang),
        list(SECTORS[lang].keys()),
        format_func=lambda x: SECTORS[lang][x],
    )

    st.divider()
    st.subheader(t("cfo_modulos", lang))
    modulos_lista = MODULES[lang]
    modulo_activo = st.radio("", modulos_lista, label_visibility="collapsed")

    st.divider()
    if st.button(t("cfo_nueva_sesion", lang), use_container_width=True):
        for key in ["messages_cfo", "orchestrator_cfo"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ── INICIALIZACIÓN ────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error(t("error_api", lang))
    st.stop()

if "orchestrator_cfo" not in st.session_state:
    st.session_state.orchestrator_cfo = CFOOrchestrator(
        api_key=api_key, mode="cfo", sector=sector, lang=lang,
    )
else:
    st.session_state.orchestrator_cfo.update_language(lang, api_key)

if "messages_cfo" not in st.session_state:
    st.session_state.messages_cfo = []

session_id = f"cfo_{nombre_cfo.lower().replace(' ', '_')}"

# ── HEADER ────────────────────────────────────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.title(t("cfo_titulo", lang))
    st.caption(f"**{nombre_cfo}** | **{empresa}** | {t('cfo_sector', lang)}: **{SECTORS[lang][sector]}**")
with col_h2:
    st.markdown(f"""
    <div style="background:#E8F5E9;border-radius:8px;padding:10px;text-align:center;margin-top:20px">
        <span style="color:#2E7D32;font-weight:bold">{t("agente_activo", lang)}</span>
    </div>""", unsafe_allow_html=True)
with col_h3:
    st.markdown(f"""
    <div style="background:#EEF2F7;border-radius:8px;padding:10px;text-align:center;margin-top:20px">
        <span style="color:#1F4E79;font-size:12px">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
    </div>""", unsafe_allow_html=True)

st.divider()

# Helper para ejecutar consultas al agente
def run_agent(query: str, spinner_key: str = "analizando") -> str:
    with st.spinner(t(spinner_key, lang)):
        result = st.session_state.orchestrator_cfo.run(
            user_message=query, session_id=session_id,
        )
    st.markdown(result["response"])
    if result.get("tools_used"):
        with st.expander(t("herramientas_usadas", lang), expanded=False):
            st.caption(f"Tools: {', '.join(result['tools_used'])} | ⏱️ {result.get('elapsed_seconds', 0)}s")
    return result["response"]

# ── MÓDULOS ───────────────────────────────────────────────────────────────────
# Detectar módulo activo por posición en la lista
mod_idx = modulos_lista.index(modulo_activo) if modulo_activo in modulos_lista else 0

# ── 0: CHAT EJECUTIVO ─────────────────────────────────────────────────────────
if mod_idx == 0:
    st.subheader(t("cfo_chat_titulo", lang))

    if not st.session_state.messages_cfo:
        with st.spinner(t("cfo_iniciando", lang)):
            greeting = get_greeting_prompt("cfo", lang)
            result = st.session_state.orchestrator_cfo.run(
                user_message=greeting, session_id=session_id,
            )
            st.session_state.messages_cfo.append({
                "role": "assistant", "content": result["response"],
                "tools": result.get("tools_used", []),
            })

    for msg in st.session_state.messages_cfo:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "💼"):
            st.markdown(msg["content"])
            if msg.get("tools") and msg["role"] == "assistant":
                with st.expander(t("herramientas_usadas", lang), expanded=False):
                    st.caption(f"Tools: {', '.join(msg['tools'])}")

    # Consultas rápidas
    label_quick = "**⚡ Consultas ejecutivas rápidas:**" if lang == "es" else "**⚡ Quick executive queries:**"
    st.markdown(label_quick)
    cols = st.columns(4)
    quick_queries = [
        (t("cfo_quick_ratios", lang),
         f"Calcula los ratios financieros clave con estos datos: activo corriente 2.5M, pasivo corriente 1.2M, ventas 8M, utilidad neta 1.2M, patrimonio 5M, EBITDA 2M, deuda financiera 3M. Empresa: {empresa}."
         if lang == "es" else
         f"Calculate key financial ratios with this data: current assets 2.5M, current liabilities 1.2M, sales 8M, net income 1.2M, equity 5M, EBITDA 2M, financial debt 3M. Company: {empresa}."),
        (t("cfo_quick_caja", lang),
         "Dame la posición de caja con: BCP S/ 850K, BBVA S/ 420K, Scotiabank S/ 180K, cobros pendientes S/ 300K, pagos pendientes S/ 450K, líneas disponibles S/ 2M."
         if lang == "es" else
         "Give me the cash position with: BCP S/ 850K, BBVA S/ 420K, Scotiabank S/ 180K, pending collections S/ 300K, pending payments S/ 450K, available lines S/ 2M."),
        (t("cfo_quick_riesgos", lang),
         f"Muéstrame la matriz de riesgos actualizada para el sector {sector}."
         if lang == "es" else
         f"Show me the updated risk matrix for the {sector} sector."),
        (t("cfo_quick_sunat", lang),
         f"¿Qué obligaciones tributarias tenemos este mes ({datetime.now().month}/{datetime.now().year})?"
         if lang == "es" else
         f"What tax obligations do we have this month ({datetime.now().month}/{datetime.now().year})?"),
    ]
    for i, (label, query) in enumerate(quick_queries):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"quick_{i}"):
                st.session_state.quick_cfo_query = query

    query = st.session_state.pop("quick_cfo_query", None)
    if prompt := (st.chat_input(t("cfo_chat_placeholder", lang)) or query):
        st.session_state.messages_cfo.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="💼"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            resp = run_agent(prompt)
        st.session_state.messages_cfo.append({
            "role": "assistant", "content": resp, "tools": [],
        })
        st.rerun()

# ── 1: ANÁLISIS FINANCIERO ────────────────────────────────────────────────────
elif mod_idx == 1:
    st.subheader(t("cfo_analisis_titulo", lang))
    st.caption(t("cfo_analisis_caption", lang))

    with st.form("form_ratios"):
        st.markdown(f"**{t('cfo_balance_titulo', lang)}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            ac = st.number_input("Activo Corriente / Current Assets (S/)", value=2_500_000.0, step=100_000.0)
            at = st.number_input("Activo Total / Total Assets (S/)", value=15_000_000.0, step=100_000.0)
        with c2:
            pc = st.number_input("Pasivo Corriente / Current Liabilities (S/)", value=1_200_000.0, step=100_000.0)
            pt = st.number_input("Pasivo Total / Total Liabilities (S/)", value=6_000_000.0, step=100_000.0)
        with c3:
            pat = st.number_input("Patrimonio / Equity (S/)", value=9_000_000.0, step=100_000.0)
            inv = st.number_input("Inventario / Inventory (S/)", value=400_000.0, step=50_000.0)

        st.markdown(f"**{t('cfo_eerr_titulo', lang)}**")
        c4, c5, c6 = st.columns(3)
        with c4:
            ven = st.number_input("Ventas / Sales (S/)", value=8_000_000.0, step=100_000.0)
            cv  = st.number_input("Costo Ventas / COGS (S/)", value=4_800_000.0, step=100_000.0)
        with c5:
            uop = st.number_input("Utilidad Operativa / EBIT (S/)", value=1_600_000.0, step=100_000.0)
            un  = st.number_input("Utilidad Neta / Net Income (S/)", value=1_200_000.0, step=100_000.0)
        with c6:
            ebitda = st.number_input("EBITDA (S/)", value=2_000_000.0, step=100_000.0)
            deuda  = st.number_input("Deuda Financiera / Financial Debt (S/)", value=3_000_000.0, step=100_000.0)

        submitted = st.form_submit_button(t("cfo_calcular_ratios", lang), type="primary", use_container_width=True)

    if submitted:
        q = (f"Calcula y analiza todos los ratios financieros: activo_corriente={ac}, pasivo_corriente={pc}, activo_total={at}, pasivo_total={pt}, patrimonio={pat}, utilidad_neta={un}, utilidad_operativa={uop}, ventas={ven}, inventario={inv}, ebitda={ebitda}, deuda_financiera={deuda}. Empresa: {empresa}. Sector: {sector}."
             if lang == "es" else
             f"Calculate and analyze all financial ratios: current_assets={ac}, current_liabilities={pc}, total_assets={at}, total_liabilities={pt}, equity={pat}, net_income={un}, operating_income={uop}, sales={ven}, inventory={inv}, ebitda={ebitda}, financial_debt={deuda}. Company: {empresa}. Sector: {sector}.")
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
                year = st.number_input("Año / Year:", value=2027, min_value=2024, max_value=2035)
                rev_base = st.number_input("Ingresos base / Base Revenue (S/):", value=8_000_000.0, step=500_000.0)
                growth = st.slider("Tasa crecimiento / Growth rate:", -0.20, 0.50, 0.08, 0.01, format="%.0f%%")
            with c2:
                cost_r = st.slider("Ratio costos / Cost ratio:", 0.30, 0.80, 0.60, 0.01, format="%.0f%%")
                opex_r = st.slider("Ratio OPEX:", 0.05, 0.40, 0.20, 0.01, format="%.0f%%")
            sub_b = st.form_submit_button(t("cfo_construir_presupuesto", lang), type="primary", use_container_width=True)
        if sub_b:
            q = (f"Construye el presupuesto anual para {year} con ingresos base {rev_base}, tasa de crecimiento {growth:.2f}, ratio costos {cost_r:.2f}, ratio opex {opex_r:.2f}, sector {sector}. Empresa: {empresa}."
                 if lang == "es" else
                 f"Build the annual budget for {year} with base revenue {rev_base}, growth rate {growth:.2f}, cost ratio {cost_r:.2f}, opex ratio {opex_r:.2f}, sector {sector}. Company: {empresa}.")
            run_agent(q, "cfo_construyendo_presupuesto")

    with tab_f:
        with st.form("form_forecast"):
            c1, c2 = st.columns(2)
            with c1:
                ytd = st.number_input("Ingresos YTD / YTD Revenue (S/):", value=4_200_000.0, step=100_000.0)
                months = st.number_input("Meses transcurridos / Months elapsed:", value=6, min_value=1, max_value=12)
            with c2:
                scenario = st.selectbox("Escenario / Scenario:", ["base", "optimista", "pesimista"])
                comm = st.slider("Variación commodity / Commodity change (%):", -0.30, 0.30, 0.0, 0.01, format="%.0f%%")
            sub_f = st.form_submit_button(t("cfo_proyectar_forecast", lang), type="primary", use_container_width=True)
        if sub_f:
            q = (f"Proyecta el forecast anual con ingresos YTD {ytd}, {months} meses transcurridos, escenario {scenario}, variación commodity {comm:.2f}. Sector: {sector}."
                 if lang == "es" else
                 f"Project the annual forecast with YTD revenue {ytd}, {months} months elapsed, scenario {scenario}, commodity change {comm:.2f}. Sector: {sector}.")
            run_agent(q, "cfo_proyectando")

    with tab_c:
        with st.form("form_capex"):
            proj_name = st.text_input(t("cfo_nombre_proyecto", lang), value="Expansión Planta Concentradora" if lang == "es" else "Concentrator Plant Expansion")
            c1, c2 = st.columns(2)
            with c1:
                inv_ini = st.number_input("Inversión inicial / Initial investment (S/):", value=5_000_000.0, step=100_000.0)
                wacc = st.slider("Tasa descuento / Discount rate (WACC):", 0.05, 0.25, 0.12, 0.01, format="%.0f%%")
                vida = st.number_input("Vida útil / Useful life (años/years):", value=5, min_value=1, max_value=20)
            with c2:
                st.markdown(t("cfo_flujos_proyectados", lang))
                flujos = [st.number_input(f"{'Año' if lang == 'es' else 'Year'} {i}:", value=1_500_000.0, step=100_000.0, key=f"fc_{i}") for i in range(1, int(vida) + 1)]
            sub_c = st.form_submit_button(t("cfo_evaluar_capex", lang), type="primary", use_container_width=True)
        if sub_c:
            q = (f"Evalúa el proyecto CAPEX '{proj_name}' con inversión {inv_ini}, flujos de caja {flujos}, tasa de descuento {wacc:.2f}, vida útil {vida} años."
                 if lang == "es" else
                 f"Evaluate the CAPEX project '{proj_name}' with investment {inv_ini}, cash flows {flujos}, discount rate {wacc:.2f}, useful life {vida} years.")
            run_agent(q, "cfo_evaluando")

# ── 3: TESORERÍA Y BANCOS ─────────────────────────────────────────────────────
elif mod_idx == 3:
    st.subheader(t("cfo_tesoreria_titulo", lang))
    tab_ca, tab_ba, tab_wc = st.tabs([t("cfo_tab_caja", lang), t("cfo_tab_bancos", lang), t("cfo_tab_wc", lang)])

    with tab_ca:
        with st.form("form_caja"):
            st.markdown(f"**{t('cfo_saldos_banco', lang)}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                bcp = st.number_input("BCP (S/):", value=850_000.0, step=10_000.0)
                bbva = st.number_input("BBVA (S/):", value=420_000.0, step=10_000.0)
            with c2:
                scot = st.number_input("Scotiabank (S/):", value=180_000.0, step=10_000.0)
                inter = st.number_input("Interbank (S/):", value=95_000.0, step=10_000.0)
            with c3:
                cobros = st.number_input("Cobros pendientes / Pending collections (S/):", value=300_000.0, step=10_000.0)
                pagos  = st.number_input("Pagos pendientes / Pending payments (S/):", value=450_000.0, step=10_000.0)
                lineas = st.number_input("Líneas disponibles / Available lines (S/):", value=2_000_000.0, step=100_000.0)
            sub_ca = st.form_submit_button(t("cfo_calcular_posicion", lang), type="primary", use_container_width=True)
        if sub_ca:
            saldos = {"BCP": bcp, "BBVA": bbva, "Scotiabank": scot, "Interbank": inter}
            q = (f"Calcula la posición de caja con saldos {json.dumps(saldos)}, cobros pendientes {cobros}, pagos pendientes {pagos}, líneas disponibles {lineas}."
                 if lang == "es" else
                 f"Calculate the cash position with balances {json.dumps(saldos)}, pending collections {cobros}, pending payments {pagos}, available lines {lineas}.")
            run_agent(q, "cfo_calculando_caja")

    with tab_ba:
        with st.form("form_banco"):
            c1, c2 = st.columns(2)
            with c1:
                banco = st.selectbox("Banco / Bank:", ["BCP", "BBVA", "Scotiabank", "Interbank", "Banco de la Nación"])
                tipo_linea_opts = {
                    "es": ["Línea de crédito revolvente", "Préstamo a plazo", "Carta fianza", "Factoring", "Leasing"],
                    "en": ["Revolving credit line", "Term loan", "Bank guarantee", "Factoring", "Leasing"],
                }
                tipo_linea = st.selectbox("Tipo de línea / Line type:", tipo_linea_opts[lang])
                monto_linea = st.number_input("Monto línea / Line amount (S/):", value=3_000_000.0, step=100_000.0)
            with c2:
                monto_usado = st.number_input("Monto utilizado / Used amount (S/):", value=1_800_000.0, step=100_000.0)
                tasa_banco = st.number_input("Tasa interés anual / Annual interest rate (%):", value=8.5, step=0.1) / 100
                vencimiento = st.date_input("Vencimiento / Maturity:")
            sub_ba = st.form_submit_button(t("cfo_analizar_linea", lang), type="primary", use_container_width=True)
        if sub_ba:
            q = (f"Analiza la línea bancaria del {banco}: tipo {tipo_linea}, monto {monto_linea}, utilizado {monto_usado}, tasa {tasa_banco:.4f}, vencimiento {vencimiento}."
                 if lang == "es" else
                 f"Analyze the bank line from {banco}: type {tipo_linea}, amount {monto_linea}, used {monto_usado}, rate {tasa_banco:.4f}, maturity {vencimiento}.")
            run_agent(q, "cfo_analizando_linea")

    with tab_wc:
        with st.form("form_wc"):
            c1, c2 = st.columns(2)
            with c1:
                cxc = st.number_input("Cuentas por cobrar / Accounts receivable (S/):", value=1_200_000.0, step=50_000.0)
                inv_wc = st.number_input("Inventario / Inventory (S/):", value=600_000.0, step=50_000.0)
                cxp = st.number_input("Cuentas por pagar / Accounts payable (S/):", value=800_000.0, step=50_000.0)
            with c2:
                ven_dia = st.number_input("Ventas diarias / Daily sales (S/):", value=22_000.0, step=1_000.0)
                costo_dia = st.number_input("Costo diario / Daily cost (S/):", value=13_000.0, step=1_000.0)
            sub_wc = st.form_submit_button(t("cfo_optimizar_wc", lang), type="primary", use_container_width=True)
        if sub_wc:
            q = (f"Optimiza el capital de trabajo: CxC {cxc}, inventario {inv_wc}, CxP {cxp}, ventas diarias {ven_dia}, costo diario {costo_dia}."
                 if lang == "es" else
                 f"Optimize working capital: AR {cxc}, inventory {inv_wc}, AP {cxp}, daily sales {ven_dia}, daily cost {costo_dia}.")
            run_agent(q, "cfo_analizando_wc")

# ── 4: GESTIÓN DE RIESGOS ─────────────────────────────────────────────────────
elif mod_idx == 4:
    st.subheader(t("cfo_riesgos_titulo", lang))
    tab_mx, tab_ri, tab_vr = st.tabs([t("cfo_tab_matriz", lang), t("cfo_tab_riesgo", lang), t("cfo_tab_var", lang)])

    with tab_mx:
        if st.button(t("cfo_cargar_matriz", lang), type="primary", use_container_width=True):
            q = (f"Muéstrame la matriz de riesgos completa para el sector {sector} con scoring y priorización."
                 if lang == "es" else
                 f"Show me the complete risk matrix for the {sector} sector with scoring and prioritization.")
            run_agent(q, "cfo_cargando_matriz")

    with tab_ri:
        with st.form("form_riesgo"):
            nombre_r = st.text_input(t("cfo_nombre_riesgo", lang), value="Caída del precio del cobre" if lang == "es" else "Copper price drop")
            c1, c2 = st.columns(2)
            with c1:
                cat = st.selectbox(t("cfo_categoria", lang), RISK_CATEGORIES[lang])
                prob = st.slider(t("cfo_probabilidad", lang), 0.0, 1.0, 0.35, 0.05, format="%.0f%%")
            with c2:
                imp = st.slider(t("cfo_impacto", lang), 0.0, 1.0, 0.30, 0.05, format="%.0f%%")
                ing = st.number_input(t("cfo_ingresos_anuales", lang), value=8_000_000.0, step=500_000.0)
            sub_ri = st.form_submit_button(t("cfo_evaluar_riesgo_btn", lang), type="primary", use_container_width=True)
        if sub_ri:
            q = (f"Evalúa el riesgo '{nombre_r}', categoría {cat}, probabilidad {prob}, impacto {imp}, ingresos anuales {ing}."
                 if lang == "es" else
                 f"Assess the risk '{nombre_r}', category {cat}, probability {prob}, impact {imp}, annual revenue {ing}.")
            run_agent(q, "cfo_calculando")

    with tab_vr:
        with st.form("form_var"):
            c1, c2 = st.columns(2)
            with c1:
                port = st.number_input("Valor portafolio / Portfolio value (S/):", value=5_000_000.0, step=100_000.0)
                vol  = st.slider("Volatilidad diaria / Daily volatility:", 0.001, 0.05, 0.015, 0.001, format="%.1f%%")
            with c2:
                conf = st.selectbox("Nivel confianza / Confidence level:", [0.90, 0.95, 0.99], index=2, format_func=lambda x: f"{x*100:.0f}%")
                hor  = st.number_input("Horizonte / Horizon (días/days):", value=1, min_value=1, max_value=30)
            sub_vr = st.form_submit_button(t("cfo_calcular_var", lang), type="primary", use_container_width=True)
        if sub_vr:
            q = (f"Calcula el Value at Risk para portafolio {port}, volatilidad diaria {vol}, nivel de confianza {conf}, horizonte {hor} días."
                 if lang == "es" else
                 f"Calculate the Value at Risk for portfolio {port}, daily volatility {vol}, confidence level {conf}, horizon {hor} days.")
            run_agent(q, "cfo_calculando")

# ── 5: IMPUESTOS ──────────────────────────────────────────────────────────────
elif mod_idx == 5:
    st.subheader(t("cfo_impuestos_titulo", lang))
    tab_ir, tab_igv, tab_cal = st.tabs([t("cfo_tab_ir", lang), t("cfo_tab_igv", lang), t("cfo_tab_calendario", lang)])

    with tab_ir:
        with st.form("form_ir"):
            c1, c2 = st.columns(2)
            with c1:
                util = st.number_input("Utilidad antes impuestos / Pre-tax income (S/):", value=1_500_000.0, step=50_000.0)
                adic = st.number_input("Adiciones / Additions (S/):", value=120_000.0, step=10_000.0)
                dedu = st.number_input("Deducciones / Deductions (S/):", value=80_000.0, step=10_000.0)
            with c2:
                pagos_c = st.number_input("Pagos a cuenta / Advance payments (S/):", value=350_000.0, step=10_000.0)
                reg = st.selectbox("Régimen / Regime:", list(TAX_REGIMES[lang].keys()),
                                   format_func=lambda x: TAX_REGIMES[lang][x])
            sub_ir = st.form_submit_button(t("cfo_calcular_ir", lang), type="primary", use_container_width=True)
        if sub_ir:
            q = (f"Calcula el Impuesto a la Renta: utilidad {util}, adiciones {adic}, deducciones {dedu}, pagos a cuenta {pagos_c}, régimen {reg}."
                 if lang == "es" else
                 f"Calculate Income Tax: pre-tax income {util}, additions {adic}, deductions {dedu}, advance payments {pagos_c}, regime {reg}.")
            run_agent(q, "cfo_calculando_ir")

    with tab_igv:
        with st.form("form_igv"):
            c1, c2 = st.columns(2)
            with c1:
                igv_v = st.number_input("IGV ventas / Sales VAT (S/):", value=288_000.0, step=10_000.0)
                igv_c = st.number_input("IGV compras / Purchase VAT (S/):", value=180_000.0, step=10_000.0)
            with c2:
                saldo_ant = st.number_input("Saldo favor anterior / Prior credit (S/):", value=0.0, step=10_000.0)
            sub_igv = st.form_submit_button(t("cfo_calcular_igv", lang), type="primary", use_container_width=True)
        if sub_igv:
            q = (f"Calcula la posición de IGV: débito fiscal {igv_v}, crédito fiscal {igv_c}, saldo anterior {saldo_ant}."
                 if lang == "es" else
                 f"Calculate the VAT position: tax debit {igv_v}, tax credit {igv_c}, prior balance {saldo_ant}.")
            run_agent(q, "cfo_calculando_igv")

    with tab_cal:
        mes_sel = st.selectbox(
            "Mes / Month:",
            list(range(1, 13)),
            index=datetime.now().month - 1,
            format_func=lambda m: datetime(2026, m, 1).strftime("%B"),
        )
        if st.button(t("cfo_ver_calendario", lang), type="primary", use_container_width=True):
            q = (f"Muéstrame el calendario tributario SUNAT para el mes {mes_sel} del año 2026, sector {sector}."
                 if lang == "es" else
                 f"Show me the SUNAT tax calendar for month {mes_sel} of 2026, sector {sector}.")
            run_agent(q, "cfo_cargando_calendario")

# ── 6: CONTROL INTERNO ────────────────────────────────────────────────────────
elif mod_idx == 6:
    st.subheader(t("cfo_control_titulo", lang))
    proceso = st.selectbox(
        t("cfo_proceso_auditar", lang),
        list(AUDIT_PROCESSES[lang].keys()),
        format_func=lambda x: AUDIT_PROCESSES[lang][x],
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t("cfo_evaluar_controles", lang), type="primary", use_container_width=True):
            q = (f"Evalúa los controles internos del proceso {proceso} en el sector {sector}. Identifica brechas y recomienda mejoras prioritarias."
                 if lang == "es" else
                 f"Evaluate the internal controls of the {proceso} process in the {sector} sector. Identify gaps and recommend priority improvements.")
            run_agent(q, "cfo_evaluando_controles")
    with c2:
        mes_reg = st.number_input(t("cfo_mes_regulatorio", lang), value=datetime.now().month, min_value=1, max_value=12)
        if st.button(t("cfo_ver_obligaciones", lang), use_container_width=True):
            q = (f"Muéstrame las obligaciones regulatorias para el mes {mes_reg}, sector {sector}, país Perú."
                 if lang == "es" else
                 f"Show me the regulatory obligations for month {mes_reg}, sector {sector}, country Peru.")
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
            logro1 = st.text_input("1:", value="Reducción de costos operativos 5%" if lang == "es" else "5% reduction in operating costs")
            logro2 = st.text_input("2:", value="Renovación línea BCP por S/ 3M" if lang == "es" else "BCP credit line renewal for S/ 3M")
            logro3 = st.text_input("3:", value="Cero observaciones en auditoría interna" if lang == "es" else "Zero findings in internal audit")
        sub_rep = st.form_submit_button(t("cfo_generar_reporte", lang), type="primary", use_container_width=True)

    if sub_rep:
        q = (f"Genera un reporte ejecutivo completo para el período {periodo} de {empresa}. KPIs: {kpi1}, {kpi2}, {kpi3}. Logros: {logro1}, {logro2}, {logro3}. Incluye análisis de variaciones vs presupuesto, top riesgos del sector {sector} y próximos pasos."
             if lang == "es" else
             f"Generate a complete executive report for period {periodo} of {empresa}. KPIs: {kpi1}, {kpi2}, {kpi3}. Achievements: {logro1}, {logro2}, {logro3}. Include variance analysis vs budget, top risks for {sector} sector and next steps.")
        st.markdown(t("cfo_reporte_titulo", lang))
        resp = run_agent(q, "cfo_generando_reporte")
        fname = f"executive_report_{periodo.replace(' ', '_')}.txt"
        st.download_button(t("descargar_reporte", lang), data=resp, file_name=fname, mime="text/plain")