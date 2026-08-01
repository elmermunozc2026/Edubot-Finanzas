"""
CFO Agent IA - Herramientas de Planeamiento Financiero
Módulo: Presupuestos, Forecasts, CAPEX, Escenarios
"""
from datetime import datetime
import json


# ─────────────────────────────────────────────────────────────────────────────
# 1. PRESUPUESTOS
# ─────────────────────────────────────────────────────────────────────────────

def build_budget(
    year: int,
    revenue_base: float,
    growth_rate: float = 0.05,
    cost_ratio: float = 0.60,
    opex_ratio: float = 0.20,
    departments: list = None,
    sector: str = "mining",
) -> dict:
    """Construye presupuesto anual con distribución mensual y por departamento."""
    if departments is None:
        departments = ["Operaciones", "Administración", "Ventas", "Finanzas"]

    revenue = revenue_base * (1 + growth_rate)
    costo_ventas = revenue * cost_ratio
    utilidad_bruta = revenue - costo_ventas
    gastos_op = revenue * opex_ratio
    ebitda = utilidad_bruta - gastos_op
    depreciacion = revenue * 0.05
    ebit = ebitda - depreciacion
    impuestos = ebit * 0.295  # IR Perú 29.5%
    utilidad_neta = ebit - impuestos

    # Distribución mensual con estacionalidad
    estacionalidad = [0.07, 0.07, 0.08, 0.08, 0.09, 0.09,
                      0.08, 0.08, 0.09, 0.09, 0.09, 0.09]

    monthly = [
        {
            "mes": datetime(year, m + 1, 1).strftime("%B"),
            "ingresos": round(revenue * estacionalidad[m], 0),
            "costos": round(costo_ventas * estacionalidad[m], 0),
            "ebitda": round(ebitda * estacionalidad[m], 0),
        }
        for m in range(12)
    ]

    # Distribución por departamento
    dept_weights = {d: 1 / len(departments) for d in departments}
    dept_budget = {
        dept: round(gastos_op * w, 0)
        for dept, w in dept_weights.items()
    }

    return {
        "año": year,
        "sector": sector,
        "resumen_anual": {
            "ingresos": round(revenue, 0),
            "costo_ventas": round(costo_ventas, 0),
            "utilidad_bruta": round(utilidad_bruta, 0),
            "margen_bruto_pct": round((utilidad_bruta / revenue) * 100, 1),
            "gastos_operativos": round(gastos_op, 0),
            "ebitda": round(ebitda, 0),
            "margen_ebitda_pct": round((ebitda / revenue) * 100, 1),
            "depreciacion": round(depreciacion, 0),
            "ebit": round(ebit, 0),
            "impuesto_renta": round(impuestos, 0),
            "utilidad_neta": round(utilidad_neta, 0),
            "margen_neto_pct": round((utilidad_neta / revenue) * 100, 1),
        },
        "distribucion_mensual": monthly,
        "presupuesto_por_departamento": dept_budget,
        "supuestos": {
            "tasa_crecimiento": f"{growth_rate * 100:.1f}%",
            "ratio_costos": f"{cost_ratio * 100:.1f}%",
            "ratio_opex": f"{opex_ratio * 100:.1f}%",
            "tasa_ir_peru": "29.5%",
        },
    }


def compare_budget_vs_actual(
    budget: dict,
    actual_revenue: float,
    actual_costs: float,
    actual_ebitda: float,
    period: str = "YTD",
) -> dict:
    """Compara presupuesto vs real y calcula variaciones."""
    budget_rev = budget.get("resumen_anual", {}).get("ingresos", 1)
    budget_cost = budget.get("resumen_anual", {}).get("costo_ventas", 1)
    budget_ebitda = budget.get("resumen_anual", {}).get("ebitda", 1)

    var_rev = actual_revenue - budget_rev
    var_cost = actual_costs - budget_cost
    var_ebitda = actual_ebitda - budget_ebitda

    return {
        "periodo": period,
        "variaciones": {
            "ingresos": {
                "presupuesto": budget_rev,
                "real": actual_revenue,
                "variacion_abs": round(var_rev, 0),
                "variacion_pct": round((var_rev / max(budget_rev, 1)) * 100, 1),
                "semaforo": "🟢" if var_rev >= 0 else "🔴",
            },
            "costos": {
                "presupuesto": budget_cost,
                "real": actual_costs,
                "variacion_abs": round(var_cost, 0),
                "variacion_pct": round((var_cost / max(budget_cost, 1)) * 100, 1),
                "semaforo": "🟢" if var_cost <= 0 else "🔴",
            },
            "ebitda": {
                "presupuesto": budget_ebitda,
                "real": actual_ebitda,
                "variacion_abs": round(var_ebitda, 0),
                "variacion_pct": round((var_ebitda / max(budget_ebitda, 1)) * 100, 1),
                "semaforo": "🟢" if var_ebitda >= 0 else "🔴",
            },
        },
        "conclusion": (
            "Desempeño por encima del presupuesto — revisar oportunidades de reinversión."
            if var_ebitda >= 0
            else "Desempeño por debajo del presupuesto — activar plan de contingencia."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. FORECASTS Y ESCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

def run_forecast(
    revenue_ytd: float,
    months_elapsed: int,
    scenario: str = "base",
    sector: str = "mining",
    commodity_price_change: float = 0.0,
) -> dict:
    """Proyecta ingresos anuales bajo escenarios base, optimista y pesimista."""
    if months_elapsed == 0:
        months_elapsed = 1

    run_rate = (revenue_ytd / months_elapsed) * 12

    adjustments = {
        "base": 1.0,
        "optimista": 1.12,
        "pesimista": 0.88,
    }

    # Ajuste por precio de commodity (relevante para minería)
    commodity_adj = 1 + (commodity_price_change * 0.6)  # elasticidad 0.6

    scenarios = {}
    for sc, adj in adjustments.items():
        projected = run_rate * adj * commodity_adj
        scenarios[sc] = {
            "ingresos_proyectados": round(projected, 0),
            "vs_run_rate": f"{((projected / run_rate) - 1) * 100:+.1f}%",
            "supuesto_clave": {
                "base": "Continuidad de tendencia actual",
                "optimista": "Mejora de precios y volumen +12%",
                "pesimista": "Contracción de mercado -12%",
            }[sc],
        }

    return {
        "run_rate_anual": round(run_rate, 0),
        "meses_transcurridos": months_elapsed,
        "ajuste_commodity": f"{commodity_price_change * 100:+.1f}%",
        "escenarios": scenarios,
        "escenario_recomendado": scenario,
        "forecast_seleccionado": scenarios[scenario]["ingresos_proyectados"],
        "confianza": "Alta" if months_elapsed >= 6 else "Media" if months_elapsed >= 3 else "Baja",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. EVALUACIÓN DE CAPEX
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_capex(
    project_name: str,
    inversion_inicial: float,
    flujos_caja: list,
    tasa_descuento: float = 0.12,
    vida_util: int = 5,
) -> dict:
    """Evalúa proyecto CAPEX: VPN, TIR, Payback, Índice de Rentabilidad."""
    # VPN (Valor Presente Neto)
    vpn = -inversion_inicial
    for i, fc in enumerate(flujos_caja[:vida_util], 1):
        vpn += fc / ((1 + tasa_descuento) ** i)

    # TIR (aproximación por bisección)
    tir = _calculate_irr([-inversion_inicial] + flujos_caja[:vida_util])

    # Payback simple
    acumulado = 0
    payback = None
    for i, fc in enumerate(flujos_caja[:vida_util], 1):
        acumulado += fc
        if acumulado >= inversion_inicial and payback is None:
            payback = i

    # Índice de Rentabilidad
    vp_flujos = sum(fc / ((1 + tasa_descuento) ** i) for i, fc in enumerate(flujos_caja[:vida_util], 1))
    ir = vp_flujos / max(inversion_inicial, 1)

    decision = "✅ APROBAR" if vpn > 0 and tir > tasa_descuento else "❌ RECHAZAR"

    return {
        "proyecto": project_name,
        "inversion_inicial": inversion_inicial,
        "vida_util_años": vida_util,
        "tasa_descuento": f"{tasa_descuento * 100:.1f}%",
        "vpn": round(vpn, 0),
        "tir": f"{tir * 100:.1f}%" if tir else "No calculable",
        "payback_años": payback if payback else f">{vida_util} años",
        "indice_rentabilidad": round(ir, 2),
        "decision": decision,
        "interpretacion": (
            f"El proyecto genera valor por S/ {vpn:,.0f}. TIR supera el costo de capital."
            if vpn > 0
            else f"El proyecto destruye valor por S/ {abs(vpn):,.0f}. No supera el costo de capital."
        ),
    }


def _calculate_irr(cash_flows: list, max_iter: int = 1000, tol: float = 1e-6) -> float:
    """Calcula TIR por método de bisección."""
    lo, hi = -0.999, 10.0
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        npv = sum(cf / ((1 + mid) ** i) for i, cf in enumerate(cash_flows))
        if abs(npv) < tol:
            return mid
        if npv > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2