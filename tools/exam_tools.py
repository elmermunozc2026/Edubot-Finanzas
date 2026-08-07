"""
CFO Agent IA - Sistema de Exámenes Mixtos
Banco de preguntas, tipos mixtos, tiempo límite y anti-copia
"""
import random
import time
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# BANCO DE PREGUNTAS DIAGNÓSTICAS (ALEATORIAS AL INICIO DE SESIÓN)
# ─────────────────────────────────────────────────────────────────────────────

DIAGNOSTIC_QUESTIONS = {
    "mining": {
        "es": [
            "¿Qué es el EBITDA y por qué es clave para una empresa minera?",
            "Si el precio del cobre cae 20%, ¿cómo impacta al flujo de caja operativo?",
            "¿Cuál es la diferencia entre Cash Cost y AISC en minería?",
            "¿Qué ratio usarías para evaluar si una minera puede pagar sus deudas a corto plazo?",
            "¿Por qué el tipo de cambio USD/PEN es un riesgo financiero para una minera peruana?",
            "¿Qué es el VPN y cómo lo usarías para evaluar un proyecto de expansión minera?",
            "¿Cuál es la diferencia entre activo corriente y activo no corriente en una minera?",
            "¿Qué significa que una empresa tenga un ratio Deuda/EBITDA de 4x?",
            "¿Cómo afecta la depreciación al flujo de caja de una empresa minera?",
            "¿Qué es el capital de trabajo y por qué es importante gestionarlo bien?",
            "¿Cuál es la diferencia entre utilidad bruta y utilidad neta?",
            "¿Qué es el ROE y qué nos dice sobre la rentabilidad de una empresa?",
            "¿Por qué una empresa minera necesita gestionar sus reservas probadas?",
            "¿Qué es el ciclo de conversión de efectivo (CCC)?",
            "¿Cómo se calcula el margen EBITDA y qué nos indica?",
        ],
        "en": [
            "What is EBITDA and why is it key for a mining company?",
            "If copper prices fall 20%, how does it impact operating cash flow?",
            "What is the difference between Cash Cost and AISC in mining?",
            "Which ratio would you use to assess if a mining company can pay its short-term debts?",
            "Why is the USD/PEN exchange rate a financial risk for a Peruvian mining company?",
            "What is NPV and how would you use it to evaluate a mining expansion project?",
            "What is the difference between current and non-current assets in a mining company?",
            "What does it mean for a company to have a Debt/EBITDA ratio of 4x?",
            "How does depreciation affect the cash flow of a mining company?",
            "What is working capital and why is it important to manage it well?",
        ],
    },
    "banking": {
        "es": [
            "¿Qué es el NIM (Net Interest Margin) y cómo afecta la rentabilidad bancaria?",
            "¿Qué significa un NPL (Non-Performing Loan) del 5% para un banco?",
            "¿Cómo funciona el ratio de capital global según Basilea III?",
            "¿Qué es el riesgo de liquidez en un banco y cómo se gestiona?",
            "¿Cuál es la diferencia entre riesgo crediticio y riesgo de mercado?",
            "¿Qué es el ROE bancario y cómo se compara con otros sectores?",
            "¿Por qué los bancos deben mantener reservas de liquidez?",
            "¿Qué es el spread bancario y cómo impacta en la rentabilidad?",
        ],
        "en": [
            "What is NIM (Net Interest Margin) and how does it affect bank profitability?",
            "What does a 5% NPL (Non-Performing Loan) ratio mean for a bank?",
            "How does the global capital ratio work under Basel III?",
            "What is liquidity risk in a bank and how is it managed?",
            "What is the difference between credit risk and market risk?",
        ],
    },
    "retail": {
        "es": [
            "¿Qué es el GMV y por qué es importante para un retailer?",
            "¿Cómo se calcula la rotación de inventario y qué nos indica?",
            "¿Qué son las ventas Same-Store Sales (SSS) y por qué importan?",
            "¿Cómo impacta la gestión del inventario en el flujo de caja de un retailer?",
            "¿Qué es el ticket promedio y cómo se puede mejorar?",
            "¿Cuál es la diferencia entre margen bruto y margen neto en retail?",
        ],
        "en": [
            "What is GMV and why is it important for a retailer?",
            "How is inventory turnover calculated and what does it indicate?",
            "What are Same-Store Sales (SSS) and why do they matter?",
            "How does inventory management impact a retailer's cash flow?",
        ],
    },
    "health": {
        "es": [
            "¿Qué es el costo por paciente y cómo se optimiza en una clínica?",
            "¿Cómo afecta la tasa de ocupación al EBITDA de un hospital?",
            "¿Qué es el costo por cama y cómo se usa para comparar hospitales?",
            "¿Por qué la gestión del inventario de medicamentos es crítica en salud?",
        ],
        "en": [
            "What is cost per patient and how is it optimized in a clinic?",
            "How does occupancy rate affect a hospital's EBITDA?",
            "What is cost per bed and how is it used to compare hospitals?",
        ],
    },
    "government": {
        "es": [
            "¿Qué es el PIM y cómo se diferencia del PIA en el sector público peruano?",
            "¿Qué significa el devengado en la ejecución presupuestal?",
            "¿Cómo se mide la ejecución presupuestal y qué porcentaje es aceptable?",
            "¿Qué es el SIAF y para qué sirve en la gestión financiera pública?",
        ],
        "en": [
            "What is PIM and how does it differ from PIA in the Peruvian public sector?",
            "What does 'accrued' mean in budget execution?",
            "How is budget execution measured and what percentage is acceptable?",
        ],
    },
}


def get_random_diagnostic_questions(sector: str = "mining", lang: str = "es", n: int = 2) -> list:
    """Retorna N preguntas diagnósticas aleatorias para el inicio de sesión."""
    bank = DIAGNOSTIC_QUESTIONS.get(sector, DIAGNOSTIC_QUESTIONS["mining"])
    questions = bank.get(lang, bank.get("es", []))
    if not questions:
        return []
    return random.sample(questions, min(n, len(questions)))


# ─────────────────────────────────────────────────────────────────────────────
# BANCO DE PREGUNTAS DE EXAMEN (TIPOS MIXTOS)
# ─────────────────────────────────────────────────────────────────────────────

EXAM_QUESTIONS = {
    "ratios_financieros": {
        "es": [
            # Tipo A: Opción múltiple (una respuesta)
            {
                "id": "rf_001", "tipo": "opcion_multiple", "dificultad": "basico",
                "pregunta": "¿Qué mide el ratio de liquidez corriente?",
                "opciones": [
                    "La rentabilidad sobre el patrimonio",
                    "La capacidad de pagar deudas a corto plazo con activos corrientes",
                    "El nivel de endeudamiento total",
                    "La eficiencia en el uso de activos"
                ],
                "respuesta_correcta": [1],
                "explicacion": "La liquidez corriente = Activo Corriente / Pasivo Corriente. Mide si la empresa puede cubrir sus obligaciones de corto plazo.",
                "tiempo_segundos": 90,
                "puntos": 1,
            },
            # Tipo B: Múltiple selección (varias respuestas)
            {
                "id": "rf_002", "tipo": "multiple_seleccion", "dificultad": "intermedio",
                "pregunta": "¿Cuáles de los siguientes son ratios de RENTABILIDAD? (Selecciona todas las correctas)",
                "opciones": ["ROE", "Liquidez corriente", "ROA", "Margen neto", "Deuda/Patrimonio"],
                "respuesta_correcta": [0, 2, 3],
                "explicacion": "ROE (Return on Equity), ROA (Return on Assets) y Margen Neto son ratios de rentabilidad. Los otros son de liquidez y solvencia.",
                "tiempo_segundos": 120,
                "puntos": 2,
            },
            # Tipo C: Respuesta de texto
            {
                "id": "rf_003", "tipo": "texto_libre", "dificultad": "intermedio",
                "pregunta": "Una empresa minera tiene: Activo Corriente S/ 2,500,000 y Pasivo Corriente S/ 1,200,000. Calcula el ratio de liquidez corriente e interpreta el resultado desde la perspectiva del CFO.",
                "respuesta_referencia": "Liquidez = 2,500,000 / 1,200,000 = 2.08. Significa que por cada sol de deuda a corto plazo, la empresa tiene S/ 2.08 de activos corrientes. Es una posición saludable (>1.5).",
                "palabras_clave": ["2.08", "liquidez", "activo corriente", "pasivo corriente"],
                "tiempo_segundos": 180,
                "puntos": 3,
            },
            {
                "id": "rf_004", "tipo": "opcion_multiple", "dificultad": "avanzado",
                "pregunta": "Una empresa tiene ROE de 8% y su costo de capital (WACC) es 12%. ¿Qué implica esto para los accionistas?",
                "opciones": [
                    "La empresa está creando valor para los accionistas",
                    "La empresa está destruyendo valor económico (EVA negativo)",
                    "La empresa está en equilibrio financiero",
                    "El ROE no tiene relación con el costo de capital"
                ],
                "respuesta_correcta": [1],
                "explicacion": "Cuando ROE < WACC, la empresa destruye valor económico. El EVA (Economic Value Added) sería negativo, lo que significa que los accionistas obtienen menos retorno del que exigen.",
                "tiempo_segundos": 120,
                "puntos": 2,
            },
            {
                "id": "rf_005", "tipo": "texto_libre", "dificultad": "avanzado",
                "pregunta": "Como CFO de una empresa minera peruana, el Directorio te pregunta: 'Nuestro Deuda/EBITDA es 3.8x y el precio del cobre cayó 15% este trimestre. ¿Qué acciones recomiendas?' Desarrolla tu respuesta ejecutiva.",
                "respuesta_referencia": "Con Deuda/EBITDA de 3.8x (cerca del límite de covenants bancarios típicos de 4x) y caída de precios, se recomienda: 1) Revisar covenants bancarios, 2) Reducir CAPEX no esencial, 3) Optimizar capital de trabajo, 4) Evaluar refinanciamiento de deuda, 5) Activar plan de contingencia de liquidez.",
                "palabras_clave": ["covenant", "capex", "liquidez", "refinanciamiento", "contingencia"],
                "tiempo_segundos": 300,
                "puntos": 5,
            },
        ],
        "en": [
            {
                "id": "rf_001_en", "tipo": "opcion_multiple", "dificultad": "basico",
                "pregunta": "What does the current ratio measure?",
                "opciones": [
                    "Return on equity",
                    "Ability to pay short-term debts with current assets",
                    "Total debt level",
                    "Asset utilization efficiency"
                ],
                "respuesta_correcta": [1],
                "explicacion": "Current ratio = Current Assets / Current Liabilities. It measures whether the company can cover its short-term obligations.",
                "tiempo_segundos": 90,
                "puntos": 1,
            },
        ],
    },
    "flujo_caja": {
        "es": [
            {
                "id": "fc_001", "tipo": "opcion_multiple", "dificultad": "basico",
                "pregunta": "¿Cuáles son los tres componentes del Estado de Flujo de Caja según NIC 7?",
                "opciones": [
                    "Activos, Pasivos y Patrimonio",
                    "Operativo, Inversión y Financiamiento",
                    "Ingresos, Costos y Utilidad",
                    "Corto, Mediano y Largo plazo"
                ],
                "respuesta_correcta": [1],
                "explicacion": "Según NIC 7, el EFC se divide en: (1) Actividades Operativas, (2) Actividades de Inversión y (3) Actividades de Financiamiento.",
                "tiempo_segundos": 90,
                "puntos": 1,
            },
            {
                "id": "fc_002", "tipo": "multiple_seleccion", "dificultad": "intermedio",
                "pregunta": "¿Cuáles de las siguientes son señales de ALERTA en el flujo de caja? (Selecciona todas las correctas)",
                "opciones": [
                    "Flujo operativo negativo por 3 trimestres consecutivos",
                    "Flujo de inversión negativo por expansión de planta",
                    "Flujo de financiamiento positivo por nuevo préstamo bancario",
                    "Flujo neto negativo con saldo de caja mínimo",
                    "Free Cash Flow positivo y creciente"
                ],
                "respuesta_correcta": [0, 3],
                "explicacion": "El flujo operativo negativo sostenido y el flujo neto negativo con caja mínima son señales críticas. El flujo de inversión negativo puede ser positivo (expansión) y el financiamiento positivo es normal.",
                "tiempo_segundos": 150,
                "puntos": 2,
            },
            {
                "id": "fc_003", "tipo": "texto_libre", "dificultad": "avanzado",
                "pregunta": "Una empresa minera reporta: Utilidad Neta S/ 1,200,000 pero Flujo Operativo de -S/ 300,000. Como CFO, ¿qué explicaciones posibles tiene esta situación y qué acciones tomarías?",
                "respuesta_referencia": "La diferencia entre utilidad y flujo operativo se explica por: aumento de cuentas por cobrar, incremento de inventarios, o reducción de cuentas por pagar. Acciones: revisar política de crédito, optimizar inventarios, renegociar plazos con proveedores.",
                "palabras_clave": ["cuentas por cobrar", "inventario", "capital de trabajo", "política de crédito"],
                "tiempo_segundos": 240,
                "puntos": 4,
            },
        ],
    },
    "presupuesto_capex": {
        "es": [
            {
                "id": "pc_001", "tipo": "opcion_multiple", "dificultad": "intermedio",
                "pregunta": "Si el VPN de un proyecto es negativo, ¿qué decisión debe tomar el CFO?",
                "opciones": [
                    "Aprobar el proyecto porque genera ingresos",
                    "Rechazar el proyecto porque destruye valor",
                    "Aprobar si la TIR supera el 10%",
                    "Depende del sector de la empresa"
                ],
                "respuesta_correcta": [1],
                "explicacion": "Un VPN negativo significa que el proyecto destruye valor: los flujos futuros descontados no cubren la inversión inicial. La regla es: VPN > 0 → Aprobar; VPN < 0 → Rechazar.",
                "tiempo_segundos": 90,
                "puntos": 1,
            },
            {
                "id": "pc_002", "tipo": "multiple_seleccion", "dificultad": "avanzado",
                "pregunta": "¿Cuáles métricas usarías para evaluar un proyecto CAPEX de S/ 5M? (Selecciona todas las relevantes)",
                "opciones": ["VPN (Valor Presente Neto)", "ROE", "TIR (Tasa Interna de Retorno)", "Payback (Período de recuperación)", "Índice de Rentabilidad"],
                "respuesta_correcta": [0, 2, 3, 4],
                "explicacion": "Para evaluar CAPEX se usan VPN, TIR, Payback e Índice de Rentabilidad. El ROE es un ratio de rentabilidad empresarial, no de evaluación de proyectos.",
                "tiempo_segundos": 120,
                "puntos": 2,
            },
            {
                "id": "pc_003", "tipo": "texto_libre", "dificultad": "avanzado",
                "pregunta": "El Directorio te presenta dos proyectos: Proyecto A (VPN=S/800K, TIR=18%, Payback=4 años) y Proyecto B (VPN=S/1.2M, TIR=14%, Payback=6 años). El WACC es 12%. ¿Cuál recomiendas y por qué?",
                "respuesta_referencia": "Ambos proyectos son viables (TIR > WACC, VPN > 0). Si hay restricción de capital, Proyecto A tiene mejor TIR y menor payback (menor riesgo). Si se busca maximizar valor absoluto, Proyecto B tiene mayor VPN. La decisión depende del horizonte de inversión y disponibilidad de caja.",
                "palabras_clave": ["VPN", "TIR", "WACC", "payback", "riesgo", "valor"],
                "tiempo_segundos": 300,
                "puntos": 5,
            },
        ],
    },
    "riesgos": {
        "es": [
            {
                "id": "ri_001", "tipo": "opcion_multiple", "dificultad": "intermedio",
                "pregunta": "En una matriz de riesgos, un riesgo con probabilidad 40% e impacto 50% tiene un score de:",
                "opciones": ["20", "90", "20%", "El score es 20 (probabilidad × impacto × 100)"],
                "respuesta_correcta": [3],
                "explicacion": "Score = Probabilidad × Impacto × 100 = 0.40 × 0.50 × 100 = 20. Un score de 20 corresponde a nivel MEDIO (15-30).",
                "tiempo_segundos": 90,
                "puntos": 1,
            },
            {
                "id": "ri_002", "tipo": "texto_libre", "dificultad": "avanzado",
                "pregunta": "Como CFO de una minera peruana, identifica los 3 principales riesgos financieros del sector y propón un plan de mitigación para cada uno.",
                "respuesta_referencia": "1) Riesgo de precio de commodity: hedging con forwards/opciones, diversificación de productos. 2) Riesgo cambiario USD/PEN: cobertura natural, deuda en USD si ingresos son en USD. 3) Riesgo de liquidez: mantener líneas de crédito comprometidas, fondo de contingencia.",
                "palabras_clave": ["commodity", "hedging", "cambiario", "cobertura", "liquidez", "contingencia"],
                "tiempo_segundos": 300,
                "puntos": 5,
            },
        ],
    },
}


def get_exam_questions(
    topic: str,
    difficulty: str = "intermedio",
    lang: str = "es",
    num_questions: int = 5,
    mix_types: bool = True,
) -> list:
    """
    Retorna preguntas de examen mezclando tipos (opción múltiple, múltiple selección, texto libre).
    """
    bank = EXAM_QUESTIONS.get(topic, EXAM_QUESTIONS.get("ratios_financieros", {}))
    questions = bank.get(lang, bank.get("es", []))

    # Filtrar por dificultad
    difficulty_order = {"basico": 0, "intermedio": 1, "avanzado": 2}
    max_level = difficulty_order.get(difficulty, 1)
    filtered = [q for q in questions if difficulty_order.get(q.get("dificultad", "intermedio"), 1) <= max_level]

    if not filtered:
        filtered = questions

    if mix_types:
        # Asegurar mezcla de tipos
        by_type = {}
        for q in filtered:
            tipo = q.get("tipo", "opcion_multiple")
            by_type.setdefault(tipo, []).append(q)

        mixed = []
        types_cycle = list(by_type.keys())
        i = 0
        while len(mixed) < num_questions and any(by_type.values()):
            tipo = types_cycle[i % len(types_cycle)]
            if by_type.get(tipo):
                q = random.choice(by_type[tipo])
                if q not in mixed:
                    mixed.append(q)
                    by_type[tipo].remove(q)
            i += 1
            if i > num_questions * 3:
                break
        return mixed[:num_questions]
    else:
        return random.sample(filtered, min(num_questions, len(filtered)))


def calculate_exam_score(questions: list, answers: dict) -> dict:
    """
    Calcula la calificación del examen.
    answers: {question_id: respuesta_del_alumno}
    """
    total_points = sum(q.get("puntos", 1) for q in questions)
    earned_points = 0
    results = []

    for q in questions:
        qid = q["id"]
        student_answer = answers.get(qid)
        correct = q.get("respuesta_correcta", [])
        tipo = q.get("tipo", "opcion_multiple")
        is_correct = False
        feedback = ""

        if tipo in ["opcion_multiple", "multiple_seleccion"]:
            if isinstance(student_answer, list):
                is_correct = sorted(student_answer) == sorted(correct)
            elif isinstance(student_answer, int):
                is_correct = [student_answer] == correct
            feedback = q.get("explicacion", "")
            if is_correct:
                earned_points += q.get("puntos", 1)

        elif tipo == "texto_libre":
            # Evaluación por palabras clave
            keywords = q.get("palabras_clave", [])
            if student_answer and keywords:
                answer_lower = str(student_answer).lower()
                matches = sum(1 for kw in keywords if kw.lower() in answer_lower)
                keyword_score = matches / len(keywords)
                partial_points = round(q.get("puntos", 1) * keyword_score, 1)
                earned_points += partial_points
                is_correct = keyword_score >= 0.5
                feedback = f"Palabras clave encontradas: {matches}/{len(keywords)}. {q.get('explicacion', '')}"
            else:
                feedback = "Respuesta no evaluada automáticamente — requiere revisión del profesor."

        results.append({
            "pregunta": q["pregunta"],
            "tipo": tipo,
            "respuesta_alumno": student_answer,
            "respuesta_correcta": correct,
            "es_correcto": is_correct,
            "puntos_obtenidos": q.get("puntos", 1) if is_correct else 0,
            "puntos_posibles": q.get("puntos", 1),
            "feedback": feedback,
        })

    score_10 = round((earned_points / max(total_points, 1)) * 10, 1)
    nivel = "Excelente" if score_10 >= 9 else "Bueno" if score_10 >= 7 else "Regular" if score_10 >= 5 else "Necesita refuerzo"

    return {
        "puntos_obtenidos": round(earned_points, 1),
        "puntos_totales": total_points,
        "calificacion_10": score_10,
        "nivel": nivel,
        "porcentaje": round((earned_points / max(total_points, 1)) * 100, 1),
        "resultados_detalle": results,
        "timestamp": datetime.now().isoformat(),
    }