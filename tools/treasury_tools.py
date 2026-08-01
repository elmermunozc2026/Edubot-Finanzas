"""
CFO Agent IA - Herramientas de Tesorería
Módulo: Gestión de Caja, Bancos, Capital de Trabajo
"""
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────────
# 1. POSICIÓN DE CAJA DIARIA
# ─────────────────────────────────────────────────────────────────────────────

def get_daily_cash_position(
    saldo_bancos: dict,
    cobros_pendientes: float = 0,
    pagos_pendientes: float = 0,
    lineas_credito_disponibles: float = 0,
) -> dict:
    """Calcula posición de caja consolidada y disponibilidad real."""
    saldo_total = sum(saldo_bancos.values())
    posicion_neta = saldo_total + cobros_pendientes - pagos_pendientes
    liquidez_total = posicion_neta + lineas_credito_disponibles

    alertas = []
    if posicion_neta < 0:
        alertas.append("🔴 CRÍTICO: Posición de caja negativa — activar líneas de crédito")
    elif posicion_neta < saldo_total * 0.1:
        alertas.append("🟡 PRECAUCIÓN: Caja mínima operativa en riesgo")
    if cobros_pendientes > saldo_total * 2:
        alertas.append("🟡 PRECAUCIÓN: Alta concentración en cuentas por cobrar")

    return {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "saldo_por_banco": saldo_bancos,
        "saldo_total_bancos": round(saldo_total, 2),
        "cobros_pendientes_48h": round(cobros_pendientes, 2),
        "pagos_pendientes_48h": round(pagos_pendientes, 2),
        "posicion_neta": round(posicion_neta, 2),
        "lineas_credito_disponibles": round(lineas_credito_disponibles, 2),
        "liquidez_total_disponible": round(liquidez_total, 2),
        "semaforo": "ROJO" if posicion_neta < 0 else "AMARILLO" if posicion_neta < saldo_total * 0.15 else "VERDE",
        "alertas": alertas if alertas else ["🟢 Posición de caja saludable"],
    }


def project_cash_flow(
    saldo_inicial: float,
    ingresos_proyectados: list,
    egresos_proyectados: list,
    dias: int = 30,
) -> dict:
    """Proyecta flujo de caja para los próximos N días."""
    proyeccion = []
    saldo = saldo_inicial
    saldo_minimo = saldo_inicial
    dia_critico = None

    for i in range(min(dias, len(ingresos_proyectados), len(egresos_proyectados))):
        ingreso = ingresos_proyectados[i]
        egreso = egresos_proyectados[i]
        saldo = saldo + ingreso - egreso
        fecha = (datetime.now() + timedelta(days=i + 1)).strftime("%Y-%m-%d")

        if saldo < saldo_minimo:
            saldo_minimo = saldo
        if saldo < 0 and dia_critico is None:
            dia_critico = fecha

        proyeccion.append({
            "fecha": fecha,
            "ingreso": round(ingreso, 0),
            "egreso": round(egreso, 0),
            "saldo_acumulado": round(saldo, 0),
            "alerta": "🔴" if saldo < 0 else "🟡" if saldo < saldo_inicial * 0.1 else "🟢",
        })

    return {
        "saldo_inicial": round(saldo_inicial, 0),
        "saldo_final_proyectado": round(saldo, 0),
        "saldo_minimo_periodo": round(saldo_minimo, 0),
        "dia_critico": dia_critico,
        "necesidad_financiamiento": round(abs(min(saldo_minimo, 0)), 0) if saldo_minimo < 0 else 0,
        "proyeccion_diaria": proyeccion,
        "recomendacion": (
            f"Gestionar línea de crédito por al menos S/ {abs(min(saldo_minimo, 0)):,.0f} antes del {dia_critico}"
            if dia_critico
            else "Flujo de caja proyectado positivo en todo el período"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. GESTIÓN BANCARIA
# ─────────────────────────────────────────────────────────────────────────────

def manage_bank_lines(
    banco: str,
    tipo_linea: str,
    monto_linea: float,
    monto_utilizado: float,
    tasa_interes: float,
    vencimiento: str,
) -> dict:
    """Gestiona líneas de crédito bancarias y calcula disponibilidad y costo."""
    disponible = monto_linea - monto_utilizado
    utilizacion_pct = (monto_utilizado / max(monto_linea, 1)) * 100
    costo_anual = monto_utilizado * tasa_interes
    costo_mensual = costo_anual / 12

    alertas = []
    if utilizacion_pct > 90:
        alertas.append(f"🔴 ALERTA: Línea {banco} al {utilizacion_pct:.0f}% de utilización")
    elif utilizacion_pct > 70:
        alertas.append(f"🟡 PRECAUCIÓN: Línea {banco} al {utilizacion_pct:.0f}% — gestionar renovación")

    try:
        dias_vencimiento = (datetime.strptime(vencimiento, "%Y-%m-%d") - datetime.now()).days
        if dias_vencimiento < 30:
            alertas.append(f"🔴 URGENTE: Línea {banco} vence en {dias_vencimiento} días")
        elif dias_vencimiento < 90:
            alertas.append(f"🟡 PRECAUCIÓN: Línea {banco} vence en {dias_vencimiento} días — iniciar renovación")
    except Exception:
        dias_vencimiento = None

    return {
        "banco": banco,
        "tipo_linea": tipo_linea,
        "monto_linea": round(monto_linea, 0),
        "monto_utilizado": round(monto_utilizado, 0),
        "disponible": round(disponible, 0),
        "utilizacion_pct": round(utilizacion_pct, 1),
        "tasa_interes_anual": f"{tasa_interes * 100:.2f}%",
        "costo_financiero_anual": round(costo_anual, 0),
        "costo_financiero_mensual": round(costo_mensual, 0),
        "vencimiento": vencimiento,
        "dias_para_vencimiento": dias_vencimiento,
        "alertas": alertas if alertas else ["🟢 Línea en condiciones normales"],
    }


def optimize_working_capital(
    cuentas_cobrar: float,
    inventario: float,
    cuentas_pagar: float,
    ventas_diarias: float,
    costo_diario: float,
) -> dict:
    """Calcula y optimiza el ciclo de conversión de efectivo."""
    dso = cuentas_cobrar / max(ventas_diarias, 1)   # Days Sales Outstanding
    dio = inventario / max(costo_diario, 1)          # Days Inventory Outstanding
    dpo = cuentas_pagar / max(costo_diario, 1)       # Days Payable Outstanding
    ccc = dso + dio - dpo                             # Cash Conversion Cycle

    # Oportunidades de mejora
    oportunidades = []
    if dso > 60:
        ahorro = (dso - 45) * ventas_diarias
        oportunidades.append(f"Reducir DSO de {dso:.0f} a 45 días libera S/ {ahorro:,.0f}")
    if dio > 45:
        ahorro = (dio - 30) * costo_diario
        oportunidades.append(f"Reducir inventario de {dio:.0f} a 30 días libera S/ {ahorro:,.0f}")
    if dpo < 30:
        mejora = (45 - dpo) * costo_diario
        oportunidades.append(f"Extender DPO de {dpo:.0f} a 45 días mejora caja en S/ {mejora:,.0f}")

    return {
        "ciclo_conversion_efectivo_dias": round(ccc, 1),
        "dso_dias_cobro": round(dso, 1),
        "dio_dias_inventario": round(dio, 1),
        "dpo_dias_pago": round(dpo, 1),
        "interpretacion": (
            f"CCC de {ccc:.0f} días — "
            + ("eficiente" if ccc < 45 else "mejorable" if ccc < 90 else "crítico — requiere acción inmediata")
        ),
        "oportunidades_mejora": oportunidades if oportunidades else ["Capital de trabajo optimizado"],
        "capital_trabajo_neto": round(cuentas_cobrar + inventario - cuentas_pagar, 0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. GESTIÓN DE IMPUESTOS (PERÚ)
# ─────────────────────────────────────────────────────────────────────────────

def get_tax_calendar(mes: int, año: int = 2026) -> dict:
    """Retorna calendario tributario SUNAT para el mes indicado (Perú)."""
    calendario = {
        1:  ["PDT 621 IGV-Renta (período diciembre)", "AFP Declaración 4to trimestre"],
        2:  ["PDT 621 IGV-Renta (período enero)", "Declaración Anual IR (inicio)"],
        3:  ["PDT 621 IGV-Renta (período febrero)", "Declaración Anual IR (vencimiento según RUC)"],
        4:  ["PDT 621 IGV-Renta (período marzo)", "PDT Planilla PLAME"],
        5:  ["PDT 621 IGV-Renta (período abril)", "Pagos a cuenta IR mensual"],
        6:  ["PDT 621 IGV-Renta (período mayo)", "Declaración semestral AFP"],
        7:  ["PDT 621 IGV-Renta (período junio)", "Revisión precios de transferencia"],
        8:  ["PDT 621 IGV-Renta (período julio)", "PDT Planilla PLAME"],
        9:  ["PDT 621 IGV-Renta (período agosto)", "Pagos a cuenta IR mensual"],
        10: ["PDT 621 IGV-Renta (período setiembre)", "Declaración 3er trimestre AFP"],
        11: ["PDT 621 IGV-Renta (período octubre)", "Revisión cierre fiscal año"],
        12: ["PDT 621 IGV-Renta (período noviembre)", "Planificación tributaria cierre año"],
    }
    return {
        "mes": datetime(año, mes, 1).strftime("%B %Y"),
        "obligaciones": calendario.get(mes, []),
        "alerta": "⚠️ Verificar fechas exactas según último dígito de RUC en cronograma SUNAT",
        "url_sunat": "https://www.sunat.gob.pe/legislacion/tributaria/cronograma.html",
    }


def calculate_income_tax(
    utilidad_antes_impuestos: float,
    adiciones: float = 0,
    deducciones: float = 0,
    pagos_cuenta_realizados: float = 0,
    regimen: str = "general",
) -> dict:
    """Calcula Impuesto a la Renta según régimen tributario peruano."""
    tasas = {"general": 0.295, "mype": 0.10, "especial": 0.015}
    tasa = tasas.get(regimen, 0.295)

    renta_neta = utilidad_antes_impuestos + adiciones - deducciones
    ir_calculado = max(renta_neta * tasa, 0)
    ir_por_pagar = max(ir_calculado - pagos_cuenta_realizados, 0)
    saldo_favor = max(pagos_cuenta_realizados - ir_calculado, 0)

    return {
        "regimen_tributario": regimen.upper(),
        "tasa_ir": f"{tasa * 100:.1f}%",
        "utilidad_contable": round(utilidad_antes_impuestos, 0),
        "adiciones": round(adiciones, 0),
        "deducciones": round(deducciones, 0),
        "renta_neta_imponible": round(renta_neta, 0),
        "ir_calculado": round(ir_calculado, 0),
        "pagos_cuenta_realizados": round(pagos_cuenta_realizados, 0),
        "ir_por_pagar": round(ir_por_pagar, 0),
        "saldo_a_favor": round(saldo_favor, 0),
        "tasa_efectiva": f"{(ir_calculado / max(utilidad_antes_impuestos, 1)) * 100:.1f}%",
        "recomendacion": (
            "Evaluar deducciones adicionales permitidas para reducir base imponible."
            if ir_calculado > utilidad_antes_impuestos * 0.25
            else "Carga tributaria dentro de rangos normales."
        ),
    }


def compute_igv_position(
    igv_ventas: float,
    igv_compras: float,
    saldo_favor_anterior: float = 0,
) -> dict:
    """Calcula posición de IGV mensual (débito vs crédito fiscal)."""
    debito_fiscal = igv_ventas
    credito_fiscal = igv_compras + saldo_favor_anterior
    igv_por_pagar = max(debito_fiscal - credito_fiscal, 0)
    nuevo_saldo_favor = max(credito_fiscal - debito_fiscal, 0)

    return {
        "tasa_igv": "18%",
        "debito_fiscal": round(debito_fiscal, 0),
        "credito_fiscal_compras": round(igv_compras, 0),
        "saldo_favor_anterior": round(saldo_favor_anterior, 0),
        "credito_fiscal_total": round(credito_fiscal, 0),
        "igv_por_pagar": round(igv_por_pagar, 0),
        "nuevo_saldo_a_favor": round(nuevo_saldo_favor, 0),
        "situacion": "Por pagar" if igv_por_pagar > 0 else "Saldo a favor",
        "alerta": (
            f"🔴 IGV por pagar: S/ {igv_por_pagar:,.0f} — provisionar antes del vencimiento"
            if igv_por_pagar > 0
            else f"🟢 Saldo a favor: S/ {nuevo_saldo_favor:,.0f} — aplicar al siguiente período"
        ),
    }