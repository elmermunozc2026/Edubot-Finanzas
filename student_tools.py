"""
CFO Agent IA - Herramientas Financieras Completas
Módulo: Ratios, KPIs, Análisis de Estados Financieros
"""
from datetime import datetime
import json


# ─────────────────────────────────────────────────────────────────────────────
# 1. RATIOS Y KPIs FINANCIEROS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_financial_ratios(
    activo_corriente: float = 0,
    pasivo_corriente: float = 1,
    activo_total: float = 0,
    pasivo_total: float = 0,
    patrimonio: float = 1,
    utilidad_neta: float = 0,
    utilidad_operativa: float = 0,
    ventas: float = 1,
    inventario: float = 0,
    cuentas_por_cobrar: float = 0,
    costo_ventas: float = 0,
    ebitda: float = 0,
    deuda_financiera: float = 0,
) -> dict:
    """Calcula ratios completos: liquidez, solvencia, rentabilidad, eficiencia."""
    try:
        ratios = {
            # LIQUIDEZ
            "liquidez_corriente": round(activo_corriente / max(pasivo_corriente, 1), 2),
            "prueba_acida": round((activo_corriente - inventario) / max(pasivo_corriente, 1), 2),
            # SOLVENCIA
            "deuda_patrimonio": round(pasivo_total / max(patrimonio, 1), 2),
            "deuda_activo": round(pasivo_total / max(activo_total, 1), 2),
            "cobertura_intereses": round(utilidad_operativa / max(deuda_financiera * 0.08, 1), 2),
            # RENTABILIDAD
            "roe": round((utilidad_neta / max(patrimonio, 1)) * 100, 2),
            "roa": round((utilidad_neta / max(activo_total, 1)) * 100, 2),
            "margen_neto": round((utilidad_neta / max(ventas, 1)) * 100, 2),
            "margen_operativo": round((utilidad_operativa / max(ventas, 1)) * 100, 2),
            "margen_ebitda": round((ebitda / max(ventas, 1)) * 100, 2),
            # EFICIENCIA
            "rotacion_inventario": round(costo_ventas / max(inventario, 1), 2),
            "dias_cobro": round((cuentas_por_cobrar / max(ventas, 1)) * 365, 1),
            "rotacion_activos": round(ventas / max(activo_total, 1), 2),
            # APALANCAMIENTO
            "deuda_ebitda": round(deuda_financiera / max(ebitda, 1), 2),
        }
        ratios["alertas"] = _generate_ratio_alerts(ratios)
        ratios["semaforo"] = _traffic_light(ratios)
        return ratios
    except Exception as e:
        return {"error": str(e)}


def _generate_ratio_alerts(ratios: dict) -> list:
    alerts = []
    if ratios.get("liquidez_corriente", 2) < 1.0:
        alerts.append("🔴 CRÍTICO: Liquidez corriente < 1.0 — riesgo de insolvencia a corto plazo")
    elif ratios.get("liquidez_corriente", 2) < 1.5:
        alerts.append("🟡 PRECAUCIÓN: Liquidez corriente entre 1.0 y 1.5 — monitorear flujo de caja")
    if ratios.get("deuda_patrimonio", 0) > 2.0:
        alerts.append("🔴 ALERTA: Deuda/Patrimonio > 2.0 — alto apalancamiento financiero")
    if ratios.get("roe", 10) < 5:
        alerts.append("🟡 PRECAUCIÓN: ROE < 5% — rentabilidad por debajo del costo de capital")
    if ratios.get("margen_neto", 10) < 0:
        alerts.append("🔴 CRÍTICO: Margen neto negativo — la empresa opera con pérdidas")
    if ratios.get("deuda_ebitda", 0) > 4:
        alerts.append("🔴 ALERTA: Deuda/EBITDA > 4x — nivel de deuda preocupante para bancos")
    if ratios.get("dias_cobro", 30) > 90:
        alerts.append("🟡 PRECAUCIÓN: Días de cobro > 90 — revisar política de crédito a clientes")
    if not alerts:
        alerts.append("🟢 OK: Todos los ratios dentro de rangos saludables")
    return alerts


def _traffic_light(ratios: dict) -> str:
    critical = sum(1 for a in ratios.get("alertas", []) if "🔴" in a)
    warning = sum(1 for a in ratios.get("alertas", []) if "🟡" in a)
    if critical > 0:
        return "ROJO"
    elif warning > 0:
        return "AMARILLO"
    return "VERDE"


# ─────────────────────────────────────────────────────────────────────────────
# 2. ANÁLISIS DE ESTADOS FINANCIEROS
# ─────────────────────────────────────────────────────────────────────────────

def analyze_financial_statement(statement_type: str, data: dict, sector: str = "mining") -> dict:
    """Analiza Balance General, Estado de Resultados o Flujo de Caja."""
    benchmarks = _get_sector_benchmarks(sector)
    if statement_type == "balance_general":
        return _analyze_balance(data, benchmarks)
    elif statement_type == "estado_resultados":
        return _analyze_income_statement(data, benchmarks)
    elif statement_type == "flujo_caja":
        return _analyze_cash_flow(data, benchmarks)
    return {"error": f"Tipo de estado no reconocido: {statement_type}"}


def _analyze_balance(data: dict, benchmarks: dict) -> dict:
    total_activo = data.get("activo_total", 0)
    total_pasivo = data.get("pasivo_total", 0)
    patrimonio = total_activo - total_pasivo
    return {
        "tipo": "Balance General",
        "total_activo": total_activo,
        "total_pasivo": total_pasivo,
        "patrimonio_calculado": patrimonio,
        "estructura_financiamiento": {
            "deuda_pct": round(total_pasivo / max(total_activo, 1) * 100, 1),
            "patrimonio_pct": round(patrimonio / max(total_activo, 1) * 100, 1),
        },
        "interpretacion": (
            "Estructura financiera sólida con predominio de capital propio."
            if patrimonio > total_pasivo
            else "Estructura con alto apalancamiento — revisar capacidad de endeudamiento."
        ),
    }


def _analyze_income_statement(data: dict, benchmarks: dict) -> dict:
    ventas = data.get("ventas", 1)
    costo = data.get("costo_ventas", 0)
    utilidad_bruta = ventas - costo
    gastos_op = data.get("gastos_operativos", 0)
    utilidad_op = utilidad_bruta - gastos_op
    utilidad_neta = data.get("utilidad_neta", utilidad_op * 0.7)
    return {
        "tipo": "Estado de Resultados",
        "ventas": ventas,
        "utilidad_bruta": utilidad_bruta,
        "margen_bruto_pct": round(utilidad_bruta / max(ventas, 1) * 100, 1),
        "utilidad_operativa": utilidad_op,
        "margen_operativo_pct": round(utilidad_op / max(ventas, 1) * 100, 1),
        "utilidad_neta": utilidad_neta,
        "margen_neto_pct": round(utilidad_neta / max(ventas, 1) * 100, 1),
        "vs_benchmark": {
            "margen_bruto_sector": benchmarks.get("margen_bruto", "N/D"),
            "margen_neto_sector": benchmarks.get("margen_neto", "N/D"),
        },
    }


def _analyze_cash_flow(data: dict, benchmarks: dict) -> dict:
    operativo = data.get("flujo_operativo", 0)
    inversion = data.get("flujo_inversion", 0)
    financiamiento = data.get("flujo_financiamiento", 0)
    flujo_neto = operativo + inversion + financiamiento
    return {
        "tipo": "Flujo de Caja",
        "flujo_operativo": operativo,
        "flujo_inversion": inversion,
        "flujo_financiamiento": financiamiento,
        "flujo_neto": flujo_neto,
        "free_cash_flow": operativo + inversion,
        "interpretacion": (
            "Generación de caja operativa positiva — empresa autosuficiente."
            if operativo > 0
            else "Flujo operativo negativo — requiere financiamiento externo."
        ),
        "alerta_liquidez": "🔴 Flujo neto negativo — revisar posición de caja" if flujo_neto < 0 else "🟢 Flujo neto positivo",
    }


def _get_sector_benchmarks(sector: str) -> dict:
    benchmarks = {
        "mining": {"margen_bruto": "45-55%", "margen_neto": "15-25%", "roe": "12-18%", "deuda_ebitda": "1.5-2.5x"},
        "banking": {"margen_bruto": "60-70%", "margen_neto": "20-30%", "roe": "15-20%", "nim": "3-5%"},
        "retail": {"margen_bruto": "25-35%", "margen_neto": "3-8%", "roe": "10-15%", "rotacion_inv": "8-12x"},
        "health": {"margen_bruto": "40-50%", "margen_neto": "8-15%", "roe": "10-14%"},
        "government": {"ejecucion_presupuestal": "85-95%", "devengado_pct": "80-90%"},
    }
    return benchmarks.get(sector, benchmarks["mining"])