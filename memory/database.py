"""
CFO Agent IA - Base de Datos de Memoria Persistente
Módulo: SQLite para historial de alumnos y sesiones CFO
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional


class StudentMemory:
    """Memoria persistente para alumnos con SQLite."""

    def __init__(self, db_path: str = "cfo_agent.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sector TEXT DEFAULT 'mining',
                profile JSON DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                topic TEXT,
                score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL DEFAULT 10.0,
                difficulty TEXT DEFAULT 'intermedio',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS cfo_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                module TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                tools_used JSON DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    # ── ALUMNOS ──────────────────────────────────────────────────────────────

    def upsert_student(self, student_id: str, name: str, sector: str = "mining") -> bool:
        try:
            self.conn.execute("""
                INSERT INTO students (id, name, sector)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    last_active = CURRENT_TIMESTAMP
            """, (student_id, name, sector))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error upsert_student: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_students(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM students ORDER BY last_active DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    # ── INTERACCIONES ────────────────────────────────────────────────────────

    def save_interaction(
        self,
        student_id: str,
        message: str,
        response: str,
        topic: str = None,
        score: float = None,
    ) -> bool:
        try:
            self.conn.execute("""
                INSERT INTO interactions (student_id, message, response, topic, score)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, message, response, topic, score))
            self.conn.execute(
                "UPDATE students SET last_active = CURRENT_TIMESTAMP WHERE id = ?",
                (student_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error save_interaction: {e}")
            return False

    def get_context(self, student_id: str, n: int = 10) -> dict:
        """Recupera contexto del alumno para el agente."""
        rows = self.conn.execute("""
            SELECT message, response, topic, score, timestamp
            FROM interactions
            WHERE student_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (student_id, n)).fetchall()

        evals = self.conn.execute("""
            SELECT topic, AVG(score) as avg_score, COUNT(*) as intentos
            FROM evaluations
            WHERE student_id = ?
            GROUP BY topic
            ORDER BY avg_score ASC
        """, (student_id,)).fetchall()

        scores = [r["score"] for r in rows if r["score"] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        level = "avanzado" if avg_score >= 8 else "intermedio" if avg_score >= 5 else "basico"

        return {
            "student_id": student_id,
            "history": [dict(r) for r in rows],
            "evaluations_by_topic": [dict(e) for e in evals],
            "avg_score": round(avg_score, 2),
            "level": level,
            "weak_topics": [dict(e)["topic"] for e in evals if dict(e)["avg_score"] < 6],
            "total_interactions": len(rows),
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
        try:
            self.conn.execute("""
                INSERT INTO evaluations (student_id, topic, score, max_score, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, topic, score, max_score, difficulty))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error save_evaluation: {e}")
            return False

    def get_class_report(self) -> dict:
        """Genera reporte completo de la clase para el profesor."""
        students = self.get_all_students()
        report = []

        for s in students:
            ctx = self.get_context(s["id"], n=50)
            evals = self.conn.execute("""
                SELECT AVG(score/max_score*10) as promedio, COUNT(*) as total_evals
                FROM evaluations WHERE student_id = ?
            """, (s["id"],)).fetchone()

            promedio = round(dict(evals)["promedio"] or 0, 1)
            semaforo = "🟢" if promedio >= 7 else "🟡" if promedio >= 5 else "🔴"

            report.append({
                "alumno": s["name"],
                "student_id": s["id"],
                "promedio": promedio,
                "semaforo": semaforo,
                "nivel": ctx["level"],
                "temas_debiles": ctx["weak_topics"],
                "total_evaluaciones": dict(evals)["total_evals"] or 0,
                "ultima_actividad": s["last_active"],
            })

        report.sort(key=lambda x: x["promedio"], reverse=True)

        return {
            "fecha_reporte": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_alumnos": len(report),
            "promedio_clase": round(sum(r["promedio"] for r in report) / max(len(report), 1), 1),
            "alumnos_en_riesgo": [r for r in report if r["semaforo"] == "🔴"],
            "alumnos_destacados": [r for r in report if r["semaforo"] == "🟢"],
            "ranking": report,
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
        try:
            self.conn.execute("""
                INSERT INTO cfo_sessions (user_id, module, query, response, tools_used)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, module, query, response, json.dumps(tools_used or [])))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error save_cfo_session: {e}")
            return False

    def get_cfo_history(self, user_id: str, module: str = None, n: int = 20) -> list:
        query = "SELECT * FROM cfo_sessions WHERE user_id = ?"
        params = [user_id]
        if module:
            query += " AND module = ?"
            params.append(module)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(n)
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.conn.close()