"""
CFO Agent IA - Base de Datos con Google Firestore
Módulo: Memoria persistente para alumnos y sesiones CFO en la nube
"""
import json
from datetime import datetime
from typing import Optional
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# CONEXIÓN A FIRESTORE
# ─────────────────────────────────────────────────────────────────────────────

def _get_firestore_client():
    """Obtiene cliente de Firestore usando credenciales de Streamlit Secrets."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            firebase_config = dict(st.secrets["firebase"])
            if "private_key" in firebase_config:
                firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)

        return firestore.client()
    except Exception as e:
        print(f"Error conectando a Firestore: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL DE MEMORIA
# ─────────────────────────────────────────────────────────────────────────────

class StudentMemory:
    """Memoria persistente para alumnos con Google Firestore."""

    def __init__(self):
        self.db = _get_firestore_client()

    # ── ALUMNOS ──────────────────────────────────────────────────────────────

    def upsert_student(self, student_id: str, name: str, sector: str = "mining") -> bool:
        """Crea o actualiza un alumno en Firestore."""
        if not self.db:
            return False
        try:
            self.db.collection("students").document(student_id).set({
                "name":        name,
                "sector":      sector,
                "last_active": datetime.now().isoformat(),
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error upsert_student: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[dict]:
        """Obtiene un alumno por su ID."""
        if not self.db:
            return None
        try:
            doc = self.db.collection("students").document(student_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception:
            return None

    def get_all_students(self) -> list:
        """Retorna todos los alumnos."""
        if not self.db:
            return []
        try:
            docs = self.db.collection("students").order_by("last_active", direction="DESCENDING").get()
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception:
            return []

    # ── INTERACCIONES ────────────────────────────────────────────────────────

    def save_interaction(
        self,
        student_id: str,
        message: str,
        response: str,
        topic: str = None,
        score: float = None,
    ) -> bool:
        """Guarda una interacción del alumno en Firestore."""
        if not self.db:
            return False
        try:
            self.db.collection("interactions").add({
                "student_id": student_id,
                "message":    message,
                "response":   response,
                "topic":      topic,
                "score":      score,
                "timestamp":  datetime.now().isoformat(),
            })
            # Actualizar última actividad del alumno
            self.db.collection("students").document(student_id).set({
                "last_active": datetime.now().isoformat()
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error save_interaction: {e}")
            return False

    def get_context(self, student_id: str, n: int = 10) -> dict:
        """Recupera contexto del alumno para el agente."""
        if not self.db:
            return {
                "student_id": student_id, "history": [], "evaluations_by_topic": [],
                "avg_score": 0, "level": "basico", "weak_topics": [], "total_interactions": 0,
            }
        try:
            # Últimas N interacciones
            interactions = (
                self.db.collection("interactions")
                .where("student_id", "==", student_id)
                .order_by("timestamp", direction="DESCENDING")
                .limit(n)
                .get()
            )
            history = [d.to_dict() for d in interactions]

            # Evaluaciones por tema
            evals = (
                self.db.collection("evaluations")
                .where("student_id", "==", student_id)
                .get()
            )
            eval_list = [d.to_dict() for d in evals]

            # Calcular promedio por tema
            topic_scores = {}
            for e in eval_list:
                topic = e.get("topic", "general")
                score = e.get("score", 0)
                max_score = e.get("max_score", 10)
                normalized = (score / max(max_score, 1)) * 10
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(normalized)

            evals_by_topic = [
                {"topic": t, "avg_score": sum(s) / len(s), "intentos": len(s)}
                for t, s in topic_scores.items()
            ]

            # Promedio general
            all_scores = [s for scores in topic_scores.values() for s in scores]
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
            level = "avanzado" if avg_score >= 8 else "intermedio" if avg_score >= 5 else "basico"
            weak_topics = [t for t, s in topic_scores.items() if sum(s) / len(s) < 6]

            return {
                "student_id":          student_id,
                "history":             history,
                "evaluations_by_topic": evals_by_topic,
                "avg_score":           round(avg_score, 2),
                "level":               level,
                "weak_topics":         weak_topics,
                "total_interactions":  len(history),
            }
        except Exception as e:
            print(f"Error get_context: {e}")
            return {
                "student_id": student_id, "history": [], "evaluations_by_topic": [],
                "avg_score": 0, "level": "basico", "weak_topics": [], "total_interactions": 0,
            }

    # ── EVALUACIONES ─────────────────────────────────────────────────────────

    def save_evaluation(
        self,
        student_id: str,
        topic: str,
        score: float,
        max_score: float = 10.0,
        difficulty: str = "intermedio",
    ) -> bool:
        """Guarda una evaluación del alumno en Firestore."""
        if not self.db:
            return False
        try:
            self.db.collection("evaluations").add({
                "student_id": student_id,
                "topic":      topic,
                "score":      score,
                "max_score":  max_score,
                "difficulty": difficulty,
                "timestamp":  datetime.now().isoformat(),
            })
            return True
        except Exception as e:
            print(f"Error save_evaluation: {e}")
            return False

    def get_class_report(self) -> dict:
        """Genera reporte completo de la clase para el profesor."""
        if not self.db:
            return {
                "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_alumnos": 0, "promedio_clase": 0,
                "alumnos_en_riesgo": [], "alumnos_destacados": [], "ranking": [],
            }
        try:
            students = self.get_all_students()
            report = []

            for s in students:
                student_id = s["id"]
                ctx = self.get_context(student_id, n=50)
                promedio = round(ctx["avg_score"], 1)
                semaforo = "🟢" if promedio >= 7 else "🟡" if promedio >= 5 else "🔴"

                # Total evaluaciones
                evals = (
                    self.db.collection("evaluations")
                    .where("student_id", "==", student_id)
                    .get()
                )
                total_evals = len(list(evals))

                report.append({
                    "alumno":             s.get("name", student_id),
                    "student_id":         student_id,
                    "promedio":           promedio,
                    "semaforo":           semaforo,
                    "nivel":              ctx["level"],
                    "temas_debiles":      ctx["weak_topics"],
                    "total_evaluaciones": total_evals,
                    "ultima_actividad":   s.get("last_active", ""),
                })

            report.sort(key=lambda x: x["promedio"], reverse=True)
            promedio_clase = round(
                sum(r["promedio"] for r in report) / max(len(report), 1), 1
            )

            return {
                "fecha_reporte":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_alumnos":     len(report),
                "promedio_clase":    promedio_clase,
                "alumnos_en_riesgo": [r for r in report if r["semaforo"] == "🔴"],
                "alumnos_destacados":[r for r in report if r["semaforo"] == "🟢"],
                "ranking":           report,
            }
        except Exception as e:
            print(f"Error get_class_report: {e}")
            return {
                "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total_alumnos": 0, "promedio_clase": 0,
                "alumnos_en_riesgo": [], "alumnos_destacados": [], "ranking": [],
            }

    # ── SESIONES CFO ─────────────────────────────────────────────────────────

    def save_cfo_session(
        self,
        user_id: str,
        module: str,
        query: str,
        response: str,
        tools_used: list = None,
    ) -> bool:
        """Guarda una sesión del CFO Asistente en Firestore."""
        if not self.db:
            return False
        try:
            self.db.collection("cfo_sessions").add({
                "user_id":    user_id,
                "module":     module,
                "query":      query,
                "response":   response,
                "tools_used": json.dumps(tools_used or []),
                "timestamp":  datetime.now().isoformat(),
            })
            return True
        except Exception as e:
            print(f"Error save_cfo_session: {e}")
            return False

    def get_cfo_history(self, user_id: str, module: str = None, n: int = 20) -> list:
        """Obtiene historial de sesiones CFO."""
        if not self.db:
            return []
        try:
            query = self.db.collection("cfo_sessions").where("user_id", "==", user_id)
            if module:
                query = query.where("module", "==", module)
            docs = query.order_by("timestamp", direction="DESCENDING").limit(n).get()
            return [d.to_dict() for d in docs]
        except Exception:
            return []

    def close(self):
        pass