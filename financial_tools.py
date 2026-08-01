"""
CFO Agent IA - Herramientas de Riesgo, Cumplimiento y Control Interno
Módulo: Gestión de Riesgos, Compliance, Control Interno, Reporting
"""
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# 1. GESTIÓN DE RIESGOS
# ─────────────────────────────────────────────────────────────────────────────

def assess_risk(
    nombre_riesgo: str,
    categoria: str,
    probabilidad: float,   # 0.0 a 1.0
    impacto: float,        # 0.0 a 1.0 (en términos de % de ingresos)
    ingresos_anuales: float = 0,
    controles_existentes: list = None,
) -> dict:
    """Evalúa un riesgo individual con scoring y pérdida esperada."""
    if controles_existentes is None:
        controles_existentes = []

    score = probabilidad * impacto * 100
    perdida_esperada = probabilidad * impacto * ingresos_anuales

    if score >= 60:
        nivel = "CRÍTICO"
        color = "🔴"
        accion = "Mitigación inmediata requerida — escalar a Directorio"
    elif score >= 30:
        nivel = "ALTO"
        color = "🟠"
        accion = "Plan de mitigación en 30 días — reportar a Gerencia"
    elif score >= 15:
        nivel = "MEDIO"
        color = "🟡"
        accion = "Monitoreo mensual — revisar controles existentes"
    else:
        nivel = "BAJO"
        color = "🟢"
        accion = "Aceptar riesgo — monitoreo trimestral"

    return {
        "riesgo": nombre_riesgo,
        "categoria": categoria,
        "probabilidad": f"{probabilidad * 100:.0f}%",
        "impacto": f"{impacto * 100:.0f}%",
        "score_riesgo": round(score, 1),
        "nivel_riesgo": f"{color} {nivel}",
        "perdida_esperada": round(perdida_esperada, 0),
        "controles_existentes": controles_existentes,
        "accion_requerida": accion,
        "fecha_evaluacion": datetime.now().strftime("%Y-%m-%d"),
    }


def get_risk_matrix(sector: str = "mining") -> dict:
    """Retorna matriz de riesgos predefinida por sector."""
    matrices = {
        "mining": [
            {"riesgo": "Caída precio del cobre/oro", "categoria": "Mercado", "prob": 0.4, "impacto": 0.35},
            {"riesgo": "Paralización operativa por conflicto social", "categoria": "Operacional", "prob": 0.25, "impacto": 0.50},
            {"riesgo": "Cambio regulatorio ambiental", "categoria": "Regulatorio", "prob": 0.30, "impacto": 0.25},
            {"riesgo": "Tipo de cambio USD/PEN adverso", "categoria": "Financiero", "prob": 0.45, "impacto": 0.20},
            {"riesgo": "Accidente laboral grave", "categoria": "Operacional", "prob": 0.15, "impacto": 0.40},
            {"riesgo": "Incumplimiento de covenants bancarios", "categoria": "Financiero", "prob": 0.20, "impacto": 0.30},
            {"riesgo": "Fraude interno o externo", "categoria": "Integridad", "prob": 0.10, "impacto": 0.25},
        ],
        "banking": [
            {"riesgo": "Incremento de morosidad (NPL)", "categoria": "Crédito", "prob": 0.35, "impacto": 0.40},
            {"riesgo": "Riesgo de liquidez sistémico", "categoria": "Liquidez", "prob": 0.15, "impacto": 0.60},
            {"riesgo": "Incumplimiento regulatorio SBS", "categoria": "Regulatorio", "prob": 0.20, "impacto": 0.45},
            {"riesgo": "Ciberataque a sistemas core", "categoria": "Tecnológico", "prob": 0.25, "impacto": 0.50},
        ],
        "retail": [
            {"riesgo": "Contracción del consumo privado", "categoria": "Mercado", "prob": 0.40, "impacto": 0.30},
            {"riesgo": "Ruptura de cadena de suministro", "categoria": "Operacional", "prob": 0.30, "impacto": 0.35},
            {"riesgo": "Pérdida de inventario (merma/robo)", "categoria": "Operacional", "prob": 0.50, "impacto": 0.15},
        ],
    }

    riesgos = matrices.get(sector, matrices["mining"])
    evaluados = []
    for r in riesgos:
        score = r["prob"] * r["impacto"] * 100
        nivel = "CRÍTICO" if score >= 60 else "ALTO" if score >= 30 else "MEDIO" if score >= 15 else "BAJO"
        evaluados.append({
            "riesgo": r["riesgo"],
            "categoria": r["categoria"],
            "probabilidad": f"{r['prob']*100:.0f}%",
            "impacto": f"{r['impacto']*100:.0f}%",
            "score": round(score, 1),
            "nivel": nivel,
        })

    evaluados.sort(key=lambda x: x["score"], reverse=True)
    return {
        "sector": sector,
        "total_riesgos": len(evaluados),
        "criticos": sum(1 for r in evaluados if r["nivel"] == "CRÍTICO"),
        "altos": sum(1 for r in evaluados if r["nivel"] == "ALTO"),
        "medios": sum(1 for r in evaluados if r["nivel"] == "MEDIO"),
        "bajos": sum(1 for r in evaluados if r["nivel"] == "BAJO"),
        "top_5_riesgos": evaluados[:5],
        "todos_los_riesgos": evaluados,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
    }


def calculate_var(
    valor_portafolio: float,
    volatilidad_diaria: float,
    nivel_confianza: float = 0.99,
    horizonte_dias: int = 1,
) -> dict:
    """Calcula Value at Risk (VaR) paramétrico."""
    import math
    # Z-scores para niveles de confianza comunes
    z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326, 0.999: 3.090}
    z = z_scores.get(nivel_confianza, 2.326)

    var_diario = valor_portafolio * volatilidad_diaria * z
    var_horizonte = var_diario * math.sqrt(horizonte_dias)
    var_pct = (var_horizonte / valor_portafolio) * 100

    return {
        "valor_portafolio": round(valor_portafolio, 0),
        "volatilidad_diaria": f"{volatilidad_diaria * 100:.2f}%",
        "nivel_confianza": f"{nivel_confianza * 100:.0f}%",
        "horizonte_dias": horizonte_dias,
        "var_absoluto": round(var_horizonte, 0),
        "var_porcentual": f"{var_pct:.2f}%",
        "interpretacion": (
            f"Con {nivel_confianza*100:.0f}% de confianza, la pérdida máxima en {horizonte_dias} día(s) "
            f"no superará S/ {var_horizonte:,.0f} ({var_pct:.2f}% del portafolio)"
        ),
        "stress_test": {
            "escenario_adverso_2sigma": round(valor_portafolio * volatilidad_diaria * 2 * math.sqrt(horizonte_dias), 0),
            "escenario_crisis_3sigma": round(valor_portafolio * volatilidad_diaria * 3 * math.sqrt(horizonte_dias), 0),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. CONTROL INTERNO Y CUMPLIMIENTO
# ─────────────────────────────────────────────────────────────────────────────

def audit_internal_controls(proceso: str, sector: str = "mining") -> dict:
    """Evalúa controles internos de un proceso y genera checklist de auditoría."""
    controles_por_proceso = {
        "cuentas_por_pagar": [
            ("Segregación de funciones: quien aprueba ≠ quien paga", True),
            ("Doble firma para pagos > umbral definido", True),
            ("Conciliación mensual con proveedores", False),
            ("Validación de facturas vs órdenes de compra", True),
            ("Revisión de proveedores en lista negra SUNAT", False),
        ],
        "cuentas_por_cobrar": [
            ("Política de crédito documentada y aprobada", True),
            ("Análisis de antigüedad de saldos mensual", True),
            ("Provisión de cobranza dudosa según NIIF 9", False),
            ("Conciliación con clientes trimestral", False),
            ("Autorización de descuentos y notas de crédito", True),
        ],
        "nomina": [
            ("Validación de altas/bajas con RRHH", True),
            ("Revisión de horas extras con supervisores", True),
            ("Conciliación planilla vs PLAME SUNAT", True),
            ("Segregación: quien calcula ≠ quien aprueba ≠ quien paga", False),
            ("Auditoría sorpresiva de planilla semestral", False),
        ],
        "tesoreria": [
            ("Conciliaciones bancarias diarias", True),
            ("Límites de autorización por monto y firmante", True),
            ("Revisión de transferencias por segunda persona", False),
            ("Política de inversiones temporales aprobada", True),
            ("Arqueo de caja chica mensual", False),
        ],
        "inventarios": [
            ("Conteo físico anual con auditores externos", True),
            ("Conteos cíclicos mensuales por categoría", False),
            ("Sistema de control de acceso al almacén", True),
            ("Conciliación sistema vs físico mensual", False),
            ("Política de obsolescencia documentada", True),
        ],
    }

    controles = controles_por_proceso.get(proceso, [
        ("Control general documentado", True),
        ("Revisión periódica por supervisión", False),
    ])

    implementados = sum(1 for _, impl in controles if impl)
    total = len(controles)
    score = (implementados / total) * 100

    brechas = [ctrl for ctrl, impl in controles if not impl]
    nivel = "FUERTE" if score >= 80 else "ADECUADO" if score >= 60 else "DÉBIL" if score >= 40 else "CRÍTICO"

    return {
        "proceso": proceso,
        "controles_evaluados": total,
        "controles_implementados": implementados,
        "score_control": f"{score:.0f}%",
        "nivel_control": nivel,
        "brechas_identificadas": brechas,
        "recomendaciones": [
            f"Implementar: {brecha}" for brecha in brechas
        ],
        "prioridad": "ALTA" if score < 60 else "MEDIA" if score < 80 else "BAJA",
        "fecha_evaluacion": datetime.now().strftime("%Y-%m-%d"),
    }


def check_regulatory_calendar(
    mes: int,
    año: int = 2026,
    pais: str = "PE",
    sector: str = "mining",
) -> dict:
    """Retorna obligaciones regulatorias del mes para el sector y país."""
    obligaciones_generales = {
        1: ["Declaración Jurada Anual IR (inicio)", "Memoria Anual Directorio"],
        2: ["PDT 621 enero", "Declaración AFP 4to trimestre"],
        3: ["Declaración Anual IR (vencimiento)", "Estados Financieros Auditados"],
        4: ["PDT 621 marzo", "Junta General de Accionistas"],
        5: ["PDT 621 abril", "Distribución de dividendos (si aplica)"],
        6: ["PDT 621 mayo", "Informe semestral a accionistas"],
        7: ["PDT 621 junio", "Revisión precios de transferencia"],
        8: ["PDT 621 julio", "Declaración AFP 2do trimestre"],
        9: ["PDT 621 agosto", "Revisión cumplimiento covenants bancarios"],
        10: ["PDT 621 setiembre", "Inicio planificación presupuesto siguiente año"],
        11: ["PDT 621 octubre", "Revisión cierre fiscal"],
        12: ["PDT 621 noviembre", "Cierre contable y ajustes NIIF", "Planificación tributaria"],
    }

    obligaciones_sector = {
        "mining": {
            3: ["Declaración Anual Ambiental (DAA) — MINEM"],
            6: ["Informe semestral de seguridad minera — OSINERGMIN"],
            9: ["Reporte de producción trimestral — MINEM"],
            12: ["Plan de cierre de minas — actualización anual"],
        },
        "banking": {
            1: ["Reporte de liquidez SBS", "Ratio de capital global"],
            4: ["Estados financieros trimestrales SBS"],
            7: ["Reporte semestral de riesgo crediticio SBS"],
            10: ["Reporte trimestral SBS"],
        },
    }

    obs = obligaciones_generales.get(mes, []).copy()
    sector_obs = obligaciones_sector.get(sector, {}).get(mes, [])
    obs.extend(sector_obs)

    return {
        "mes": datetime(año, mes, 1).strftime("%B %Y"),
        "pais": pais,
        "sector": sector,
        "obligaciones": obs,
        "total_obligaciones": len(obs),
        "alerta": f"⚠️ {len(obs)} obligaciones regulatorias este mes — verificar fechas exactas",
        "nota": "Confirmar fechas según cronograma oficial SUNAT y reguladores sectoriales",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. REPORTING A MATRIZ / DIRECTORIO
# ─────────────────────────────────────────────────────────────────────────────

def generate_executive_summary(
    periodo: str,
    kpis: dict,
    variaciones_presupuesto: dict,
    top_riesgos: list,
    logros: list,
    proximos_pasos: list,
    formato: str = "narrativo",
) -> dict:
    """Genera resumen ejecutivo estructurado para reporte a Directorio o Matriz."""
    semaforo_general = "VERDE"
    if any("🔴" in str(v) for v in variaciones_presupuesto.values()):
        semaforo_general = "ROJO"
    elif any("🟡" in str(v) for v in variaciones_presupuesto.values()):
        semaforo_general = "AMARILLO"

    narrativa = f"""
RESUMEN EJECUTIVO — {periodo}
Estado General: {semaforo_general}

DESEMPEÑO FINANCIERO:
{chr(10).join(f'• {k}: {v}' for k, v in kpis.items())}

VARIACIONES VS PRESUPUESTO:
{chr(10).join(f'• {k}: {v}' for k, v in variaciones_presupuesto.items())}

PRINCIPALES RIESGOS:
{chr(10).join(f'• {r}' for r in top_riesgos)}

LOGROS DEL PERÍODO:
{chr(10).join(f'• {l}' for l in logros)}

PRÓXIMOS PASOS:
{chr(10).join(f'• {p}' for p in proximos_pasos)}
""".strip()

    return {
        "periodo": periodo,
        "semaforo_general": semaforo_general,
        "kpis_clave": kpis,
        "variaciones_presupuesto": variaciones_presupuesto,
        "top_riesgos": top_riesgos,
        "logros": logros,
        "proximos_pasos": proximos_pasos,
        "narrativa_ejecutiva": narrativa,
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "listo_para_directorio": True,
    }