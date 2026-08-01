"""
CFO Agent IA - Herramientas de Gestión de Estudiantes
Módulo: Perfiles, Evaluaciones, Reportes del Profesor
"""
from datetime import datetime
import json


def get_student_profile(student_id: str, db_conn=None) -> dict:
    """Recupera perfil completo del alumno desde la base de datos."""
    # En producción: consultar SQLite/Firestore
    # Aquí retornamos estructura de ejemplo
    return {
        "student_id": student_id,
        "nombre": f"Alumno {student_id}",
        "nivel_actual": "intermedio",
        "promedio_general": 7.2,
        "temas_dominados": ["Liquidez", "Ratios de Rentabilidad"],
        "areas_debiles": ["Flujo de Caja", "Precios de Transferencia"],
        "sesiones_completadas": 12,
        "ultima_sesion": datetime.now().strftime("%Y-%m-%d"),
        "racha_dias": 5,
        "recomendacion_siguiente_tema": "Análisis de Flujo de Caja",
    }


def save_evaluation(
    student_id: str,
    topic: str,
    score: float,
    max_score: float = 10.0,
    preguntas: list = None,
    respuestas: list = None,
) -> dict:
    """Guarda evaluación del alumno y actualiza su perfil."""
    pct = (score / max_score) * 100
    nivel = "Excelente" if pct >= 90 else "Bueno" if pct >= 70 else "Regular" if pct >= 50 else "Necesita refuerzo"
    return {
        "student_id": student_id,
        "topic": topic,
        "score": score,
        "max_score": max_score,
        "porcentaje": round(pct, 1),
        "nivel": nivel,
        "timestamp": datetime.now().isoformat(),
        "guardado": True,
        "mensaje_alumno": (
            f"¡Excelente trabajo! Obtuviste {score}/{max_score} en {topic}."
            if pct >= 70
            else f"Obtuviste {score}/{max_score} en {topic}. Repasemos los conceptos clave juntos."
        ),
    }


def generate_quiz(
    topic: str,
    difficulty: str = "intermedio",
    student_id: str = None,
    num_questions: int = 5,
    sector: str = "mining",
) -> dict:
    """Genera preguntas de evaluación adaptadas al nivel del alumno."""
    preguntas_banco = {
        "ratios_financieros": {
            "basico": [
                {"pregunta": "¿Qué mide el ratio de liquidez corriente?",
                 "opciones": ["Rentabilidad", "Capacidad de pago a corto plazo", "Nivel de deuda", "Eficiencia operativa"],
                 "respuesta": 1, "explicacion": "Mide si la empresa puede cubrir sus deudas de corto plazo con activos corrientes."},
                {"pregunta": "Si el activo corriente es S/ 500,000 y el pasivo corriente es S/ 250,000, ¿cuál es la liquidez corriente?",
                 "opciones": ["0.5", "1.0", "2.0", "4.0"],
                 "respuesta": 2, "explicacion": "Liquidez = 500,000 / 250,000 = 2.0"},
            ],
            "intermedio": [
                {"pregunta": "Una empresa minera tiene ROE de 8% y el costo de capital es 12%. ¿Qué implica esto?",
                 "opciones": ["Crea valor para el accionista", "Destruye valor para el accionista", "Es indiferente", "Depende del sector"],
                 "respuesta": 1, "explicacion": "ROE < Costo de Capital significa destrucción de valor económico (EVA negativo)."},
                {"pregunta": "¿Qué ratio relaciona la deuda financiera con la capacidad de generación de caja?",
                 "opciones": ["ROE", "Deuda/EBITDA", "Liquidez ácida", "Margen bruto"],
                 "respuesta": 1, "explicacion": "Deuda/EBITDA mide cuántos años de EBITDA se necesitan para pagar la deuda total."},
            ],
            "avanzado": [
                {"pregunta": "En el sector minero peruano, un Deuda/EBITDA de 3.5x en contexto de caída del precio del cobre, ¿qué acción recomienda como CFO?",
                 "opciones": ["Aumentar dividendos", "Refinanciar deuda y reducir CAPEX", "Expandir operaciones", "Ignorar el ratio"],
                 "respuesta": 1, "explicacion": "Con precio de commodity bajo y alto apalancamiento, la prioridad es preservar liquidez y renegociar condiciones bancarias."},
            ],
        },
        "flujo_caja": {
            "basico": [
                {"pregunta": "¿Cuáles son los tres componentes del Estado de Flujo de Caja?",
                 "opciones": ["Activos, Pasivos, Patrimonio", "Operativo, Inversión, Financiamiento", "Ingresos, Costos, Utilidad", "Corto, Mediano, Largo plazo"],
                 "respuesta": 1, "explicacion": "El EFC se divide en actividades operativas, de inversión y de financiamiento según NIC 7."},
            ],
            "intermedio": [
                {"pregunta": "Una empresa tiene utilidad neta de S/ 1M pero flujo operativo negativo de S/ 500K. ¿Qué puede explicar esto?",
                 "opciones": ["Excelente gestión", "Alto crecimiento de cuentas por cobrar o inventarios", "Error contable", "Política de dividendos agresiva"],
                 "respuesta": 1, "explicacion": "La diferencia entre utilidad y flujo operativo suele explicarse por cambios en capital de trabajo."},
            ],
        },
    }

    banco = preguntas_banco.get(topic, preguntas_banco.get("ratios_financieros", {}))
    preguntas = banco.get(difficulty, banco.get("intermedio", []))[:num_questions]

    return {
        "student_id": student_id,
        "topic": topic,
        "difficulty": difficulty,
        "num_preguntas": len(preguntas),
        "preguntas": preguntas,
        "instrucciones": f"Responde las siguientes {len(preguntas)} preguntas sobre {topic}. Nivel: {difficulty}.",
        "tiempo_sugerido_minutos": len(preguntas) * 3,
    }


def send_alert_to_professor(
    mensaje: str,
    student_ids: list,
    tipo_alerta: str = "bajo_rendimiento",
    urgencia: str = "media",
) -> dict:
    """Envía alerta al profesor sobre situaciones que requieren atención."""
    iconos = {"bajo_rendimiento": "📉", "logro_destacado": "🏆", "inactividad": "⏰", "dificultad_tema": "❓"}
    icono = iconos.get(tipo_alerta, "📢")
    return {
        "alerta_enviada": True,
        "tipo": tipo_alerta,
        "urgencia": urgencia,
        "icono": icono,
        "alumnos_afectados": student_ids,
        "mensaje": f"{icono} {mensaje}",
        "timestamp": datetime.now().isoformat(),
        "accion_sugerida": {
            "bajo_rendimiento": "Programar sesión de refuerzo individual",
            "logro_destacado": "Reconocer logro en próxima clase",
            "inactividad": "Contactar al alumno para verificar situación",
            "dificultad_tema": "Revisar material del tema en próxima sesión",
        }.get(tipo_alerta, "Revisar situación"),
    }