"""
CFO Agent IA - Sistema de Autenticación y Gestión de Usuarios
Módulo: Login, Roles, Gestión de usuarios desde la app
"""
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# ROLES DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

ROLES = {
    "admin":    {"label_es": "Administrador", "label_en": "Administrator", "page": "app",             "icon": "⚙️"},
    "alumno":   {"label_es": "Alumno",         "label_en": "Student",       "page": "1_Alumno",        "icon": "🎓"},
    "profesor": {"label_es": "Profesor",       "label_en": "Teacher",       "page": "2_Profesor",      "icon": "👨‍🏫"},
    "cfo":      {"label_es": "CFO / Gerente",  "label_en": "CFO / Manager", "page": "3_CFO_Asistente", "icon": "💼"},
}

SECTORS = ["mining", "banking", "retail", "health", "government"]


# ─────────────────────────────────────────────────────────────────────────────
# BASE DE DATOS DE USUARIOS
# ─────────────────────────────────────────────────────────────────────────────

class AuthManager:
    """Gestiona autenticación, sesiones y administración de usuarios."""

    def __init__(self, db_path: str = "cfo_agent_users.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._create_default_admin()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    UNIQUE NOT NULL,
                name        TEXT    NOT NULL,
                password    TEXT    NOT NULL,
                role        TEXT    NOT NULL DEFAULT 'alumno',
                sector      TEXT    NOT NULL DEFAULT 'mining',
                active      INTEGER NOT NULL DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login  TIMESTAMP,
                created_by  TEXT    DEFAULT 'system'
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                token       TEXT    UNIQUE NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at  TIMESTAMP NOT NULL,
                active      INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS login_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    NOT NULL,
                success     INTEGER NOT NULL,
                ip_hint     TEXT,
                timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def _create_default_admin(self):
        """Crea el usuario admin por defecto si no existe."""
        existing = self.conn.execute(
            "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
        ).fetchone()
        if not existing:
            self.conn.execute("""
                INSERT INTO users (email, name, password, role, sector, created_by)
                VALUES (?, ?, ?, 'admin', 'mining', 'system')
            """, ("admin@cfoagent.ia", "Administrador CFO", self._hash_password("Admin2026!")))
            self.conn.commit()

    # ── UTILIDADES ────────────────────────────────────────────────────────────

    def _hash_password(self, password: str) -> str:
        """Hash SHA-256 con salt fijo del sistema."""
        salt = "CFOAgentIA_2026_SecureS@lt"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def _generate_token(self) -> str:
        """Genera token de sesión seguro."""
        return secrets.token_urlsafe(32)

    def _generate_temp_password(self, length: int = 10) -> str:
        """Genera contraseña temporal segura."""
        chars = string.ascii_letters + string.digits + "!@#$"
        return ''.join(secrets.choice(chars) for _ in range(length))

    # ── AUTENTICACIÓN ─────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> dict:
        """
        Autentica al usuario y retorna resultado con token de sesión.
        Returns: {"success": bool, "user": dict|None, "message": str, "token": str|None}
        """
        email = email.strip().lower()
        user = self.conn.execute(
            "SELECT * FROM users WHERE email = ? AND active = 1", (email,)
        ).fetchone()

        if not user:
            self._log_login(email, False)
            return {"success": False, "user": None, "message": "Usuario no encontrado o inactivo.", "token": None}

        if user["password"] != self._hash_password(password):
            self._log_login(email, False)
            return {"success": False, "user": None, "message": "Contraseña incorrecta.", "token": None}

        # Crear token de sesión (expira en 8 horas)
        token = self._generate_token()
        expires = datetime.now() + timedelta(hours=8)
        self.conn.execute("""
            INSERT INTO sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        """, (user["id"], token, expires.isoformat()))
        self.conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],)
        )
        self.conn.commit()
        self._log_login(email, True)

        return {
            "success": True,
            "user": dict(user),
            "message": f"Bienvenido/a, {user['name']}",
            "token": token,
        }

    def logout(self, token: str) -> bool:
        """Invalida el token de sesión."""
        self.conn.execute(
            "UPDATE sessions SET active = 0 WHERE token = ?", (token,)
        )
        self.conn.commit()
        return True

    def validate_session(self, token: str) -> Optional[dict]:
        """Valida token y retorna usuario si la sesión es válida."""
        if not token:
            return None
        row = self.conn.execute("""
            SELECT u.* FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.token = ? AND s.active = 1
              AND s.expires_at > CURRENT_TIMESTAMP
              AND u.active = 1
        """, (token,)).fetchone()
        return dict(row) if row else None

    def _log_login(self, email: str, success: bool):
        self.conn.execute(
            "INSERT INTO login_log (email, success) VALUES (?, ?)", (email, int(success))
        )
        self.conn.commit()

    # ── GESTIÓN DE USUARIOS ───────────────────────────────────────────────────

    def create_user(
        self,
        email: str,
        name: str,
        role: str,
        sector: str = "mining",
        password: str = None,
        created_by: str = "admin",
    ) -> dict:
        """Crea un nuevo usuario. Si no se provee password, genera uno temporal."""
        email = email.strip().lower()

        # Verificar si ya existe
        existing = self.conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            return {"success": False, "message": f"El email {email} ya está registrado."}

        temp_password = password or self._generate_temp_password()
        try:
            self.conn.execute("""
                INSERT INTO users (email, name, password, role, sector, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, name, self._hash_password(temp_password), role, sector, created_by))
            self.conn.commit()
            return {
                "success": True,
                "message": f"Usuario {name} creado exitosamente.",
                "temp_password": temp_password,
                "email": email,
            }
        except Exception as e:
            return {"success": False, "message": f"Error al crear usuario: {e}"}

    def update_user(self, user_id: int, **kwargs) -> dict:
        """Actualiza campos del usuario (name, role, sector, active)."""
        allowed = {"name", "role", "sector", "active"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return {"success": False, "message": "No hay campos válidos para actualizar."}
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        self.conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return {"success": True, "message": "Usuario actualizado."}

    def reset_password(self, user_id: int, new_password: str = None) -> dict:
        """Resetea la contraseña del usuario."""
        temp = new_password or self._generate_temp_password()
        self.conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (self._hash_password(temp), user_id)
        )
        self.conn.commit()
        return {"success": True, "new_password": temp, "message": "Contraseña reseteada."}

    def change_password(self, user_id: int, old_password: str, new_password: str) -> dict:
        """Permite al usuario cambiar su propia contraseña."""
        user = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return {"success": False, "message": "Usuario no encontrado."}
        if user["password"] != self._hash_password(old_password):
            return {"success": False, "message": "Contraseña actual incorrecta."}
        if len(new_password) < 8:
            return {"success": False, "message": "La nueva contraseña debe tener al menos 8 caracteres."}
        self.conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (self._hash_password(new_password), user_id)
        )
        self.conn.commit()
        return {"success": True, "message": "Contraseña actualizada exitosamente."}

    def deactivate_user(self, user_id: int) -> dict:
        """Desactiva un usuario (no lo elimina)."""
        self.conn.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))
        self.conn.execute(
            "UPDATE sessions SET active = 0 WHERE user_id = ?", (user_id,)
        )
        self.conn.commit()
        return {"success": True, "message": "Usuario desactivado."}

    def get_all_users(self) -> list:
        """Retorna todos los usuarios para el panel de administración."""
        rows = self.conn.execute("""
            SELECT id, email, name, role, sector, active, created_at, last_login, created_by
            FROM users ORDER BY role, name
        """).fetchall()
        return [dict(r) for r in rows]

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def get_login_stats(self) -> dict:
        """Estadísticas de acceso para el admin."""
        total = self.conn.execute("SELECT COUNT(*) as c FROM users WHERE active = 1").fetchone()["c"]
        by_role = self.conn.execute("""
            SELECT role, COUNT(*) as c FROM users WHERE active = 1 GROUP BY role
        """).fetchall()
        recent_logins = self.conn.execute("""
            SELECT u.name, u.role, u.last_login FROM users u
            WHERE u.last_login IS NOT NULL ORDER BY u.last_login DESC LIMIT 10
        """).fetchall()
        failed_today = self.conn.execute("""
            SELECT COUNT(*) as c FROM login_log
            WHERE success = 0 AND date(timestamp) = date('now')
        """).fetchone()["c"]
        return {
            "total_active_users": total,
            "by_role": {r["role"]: r["c"] for r in by_role},
            "recent_logins": [dict(r) for r in recent_logins],
            "failed_logins_today": failed_today,
        }

    def close(self):
        self.conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE STREAMLIT SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def init_auth():
    """Inicializa el AuthManager en session_state."""
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    return st.session_state.auth_manager


def is_authenticated() -> bool:
    """Verifica si hay una sesión activa válida."""
    token = st.session_state.get("auth_token")
    if not token:
        return False
    auth = init_auth()
    user = auth.validate_session(token)
    if user:
        st.session_state["current_user"] = user
        return True
    # Token expirado o inválido
    st.session_state.pop("auth_token", None)
    st.session_state.pop("current_user", None)
    return False


def get_current_user() -> Optional[dict]:
    """Retorna el usuario actual de la sesión."""
    return st.session_state.get("current_user")


def require_auth(allowed_roles: list = None):
    """
    Decorator/guard para páginas protegidas.
    Si no está autenticado → redirige al login.
    Si no tiene el rol → muestra error de acceso.
    """
    if not is_authenticated():
        st.switch_page("login.py")
        st.stop()

    user = get_current_user()
    if allowed_roles and user["role"] not in allowed_roles:
        st.error(f"⛔ Acceso denegado. Esta sección es solo para: {', '.join(allowed_roles)}")
        st.stop()

    return user


def logout_user():
    """Cierra la sesión del usuario actual."""
    token = st.session_state.get("auth_token")
    if token:
        auth = init_auth()
        auth.logout(token)
    for key in ["auth_token", "current_user", "orchestrator_alumno",
                "orchestrator_profesor", "orchestrator_cfo",
                "messages_alumno", "messages_profesor", "messages_cfo"]:
        st.session_state.pop(key, None)
