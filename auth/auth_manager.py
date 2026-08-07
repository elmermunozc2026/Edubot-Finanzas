"""
CFO Agent IA - Sistema de Autenticación con Google Firestore
Módulo: Login, Roles, Gestión de usuarios persistente en la nube
"""
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
    "admin":    {"label_es": "Administrador", "label_en": "Administrator", "page": "pages/0_Admin.py",            "icon": "⚙️"},
    "alumno":   {"label_es": "Alumno",         "label_en": "Student",       "page": "pages/1_Alumno.py",           "icon": "🎓"},
    "profesor": {"label_es": "Profesor",       "label_en": "Teacher",       "page": "pages/2_Profesor.py",         "icon": "👨‍🏫"},
    "cfo":      {"label_es": "CFO / Gerente",  "label_en": "CFO / Manager", "page": "pages/3_CFO_Asistente.py",   "icon": "💼"},
}

SECTORS = ["mining", "banking", "retail", "health", "government"]


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
            # Corregir saltos de línea en private_key
            if "private_key" in firebase_config:
                firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)

        return firestore.client()
    except Exception as e:
        st.error(f"Error conectando a Firestore: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL DE AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

class AuthManager:
    """Gestiona autenticación, sesiones y administración de usuarios con Firestore."""

    def __init__(self):
        self.db = _get_firestore_client()
        self._ensure_admin_exists()

    def _ensure_admin_exists(self):
        """Crea el usuario admin por defecto si no existe en Firestore."""
        if not self.db:
            return
        try:
            admin_ref = self.db.collection("users").where("role", "==", "admin").limit(1).get()
            if not list(admin_ref):
                self.db.collection("users").document("admin_default").set({
                    "email":      "admin@cfoagent.ia",
                    "name":       "Administrador CFO",
                    "password":   self._hash_password("Admin2026!"),
                    "role":       "admin",
                    "sector":     "mining",
                    "active":     True,
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "created_by": "system",
                })
        except Exception as e:
            print(f"Error _ensure_admin_exists: {e}")

    # ── UTILIDADES ────────────────────────────────────────────────────────────

    def _hash_password(self, password: str) -> str:
        salt = "CFOAgentIA_2026_SecureS@lt"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _generate_temp_password(self, length: int = 10) -> str:
        chars = string.ascii_letters + string.digits + "!@#$"
        return ''.join(secrets.choice(chars) for _ in range(length))

    # ── AUTENTICACIÓN ─────────────────────────────────────────────────────────

    def login(self, email: str, password: str) -> dict:
        """Autentica al usuario contra Firestore."""
        if not self.db:
            return {"success": False, "user": None, "message": "Error de conexión a la base de datos.", "token": None}

        email = email.strip().lower()
        try:
            users = self.db.collection("users").where("email", "==", email).where("active", "==", True).limit(1).get()
            user_list = list(users)

            if not user_list:
                self._log_login(email, False)
                return {"success": False, "user": None, "message": "Usuario no encontrado o inactivo.", "token": None}

            user_doc = user_list[0]
            user_data = user_doc.to_dict()
            user_data["id"] = user_doc.id

            if user_data.get("password") != self._hash_password(password):
                self._log_login(email, False)
                return {"success": False, "user": None, "message": "Contraseña incorrecta.", "token": None}

            # Crear token de sesión
            token = self._generate_token()
            expires = datetime.now() + timedelta(hours=8)

            self.db.collection("sessions").document(token).set({
                "user_id":    user_doc.id,
                "email":      email,
                "created_at": datetime.now().isoformat(),
                "expires_at": expires.isoformat(),
                "active":     True,
            })

            # Actualizar último login
            self.db.collection("users").document(user_doc.id).update({
                "last_login": datetime.now().isoformat()
            })

            self._log_login(email, True)

            return {
                "success": True,
                "user":    user_data,
                "message": f"Bienvenido/a, {user_data['name']}",
                "token":   token,
            }
        except Exception as e:
            return {"success": False, "user": None, "message": f"Error de autenticación: {e}", "token": None}

    def logout(self, token: str) -> bool:
        """Invalida el token de sesión en Firestore."""
        if not self.db or not token:
            return False
        try:
            self.db.collection("sessions").document(token).update({"active": False})
            return True
        except Exception:
            return False

    def validate_session(self, token: str) -> Optional[dict]:
        """Valida token y retorna usuario si la sesión es válida."""
        if not self.db or not token:
            return None
        try:
            session_doc = self.db.collection("sessions").document(token).get()
            if not session_doc.exists:
                return None

            session = session_doc.to_dict()
            if not session.get("active"):
                return None

            # Verificar expiración
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now() > expires_at:
                self.db.collection("sessions").document(token).update({"active": False})
                return None

            # Obtener usuario
            user_doc = self.db.collection("users").document(session["user_id"]).get()
            if not user_doc.exists:
                return None

            user_data = user_doc.to_dict()
            user_data["id"] = user_doc.id

            if not user_data.get("active"):
                return None

            return user_data
        except Exception:
            return None

    def _log_login(self, email: str, success: bool):
        """Registra intento de login en Firestore."""
        if not self.db:
            return
        try:
            self.db.collection("login_log").add({
                "email":     email,
                "success":   success,
                "timestamp": datetime.now().isoformat(),
            })
        except Exception:
            pass

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
        """Crea un nuevo usuario en Firestore."""
        if not self.db:
            return {"success": False, "message": "Error de conexión."}

        email = email.strip().lower()
        try:
            # Verificar si ya existe
            existing = self.db.collection("users").where("email", "==", email).limit(1).get()
            if list(existing):
                return {"success": False, "message": f"El email {email} ya está registrado."}

            temp_password = password or self._generate_temp_password()
            doc_ref = self.db.collection("users").add({
                "email":      email,
                "name":       name,
                "password":   self._hash_password(temp_password),
                "role":       role,
                "sector":     sector,
                "active":     True,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "created_by": created_by,
            })

            return {
                "success":       True,
                "message":       f"Usuario {name} creado exitosamente.",
                "temp_password": temp_password,
                "email":         email,
            }
        except Exception as e:
            return {"success": False, "message": f"Error al crear usuario: {e}"}

    def update_user(self, user_id: str, **kwargs) -> dict:
        """Actualiza campos del usuario en Firestore."""
        if not self.db:
            return {"success": False, "message": "Error de conexión."}
        allowed = {"name", "role", "sector", "active"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return {"success": False, "message": "No hay campos válidos para actualizar."}
        try:
            self.db.collection("users").document(user_id).update(updates)
            return {"success": True, "message": "Usuario actualizado."}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def reset_password(self, user_id: str, new_password: str = None) -> dict:
        """Resetea la contraseña del usuario."""
        if not self.db:
            return {"success": False, "message": "Error de conexión."}
        temp = new_password or self._generate_temp_password()
        try:
            self.db.collection("users").document(user_id).update({
                "password": self._hash_password(temp)
            })
            return {"success": True, "new_password": temp, "message": "Contraseña reseteada."}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def change_password(self, user_id: str, old_password: str, new_password: str) -> dict:
        """Permite al usuario cambiar su propia contraseña."""
        if not self.db:
            return {"success": False, "message": "Error de conexión."}
        try:
            user_doc = self.db.collection("users").document(user_id).get()
            if not user_doc.exists:
                return {"success": False, "message": "Usuario no encontrado."}
            user_data = user_doc.to_dict()
            if user_data.get("password") != self._hash_password(old_password):
                return {"success": False, "message": "Contraseña actual incorrecta."}
            if len(new_password) < 8:
                return {"success": False, "message": "La nueva contraseña debe tener al menos 8 caracteres."}
            self.db.collection("users").document(user_id).update({
                "password": self._hash_password(new_password)
            })
            return {"success": True, "message": "Contraseña actualizada exitosamente."}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def deactivate_user(self, user_id: str) -> dict:
        """Desactiva un usuario."""
        if not self.db:
            return {"success": False, "message": "Error de conexión."}
        try:
            self.db.collection("users").document(user_id).update({"active": False})
            # Invalidar sesiones activas
            sessions = self.db.collection("sessions").where("user_id", "==", user_id).where("active", "==", True).get()
            for s in sessions:
                s.reference.update({"active": False})
            return {"success": True, "message": "Usuario desactivado."}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def get_all_users(self) -> list:
        """Retorna todos los usuarios para el panel de administración."""
        if not self.db:
            return []
        try:
            users = self.db.collection("users").order_by("role").get()
            result = []
            for u in users:
                data = u.to_dict()
                data["id"] = u.id
                result.append(data)
            return result
        except Exception:
            return []

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Retorna un usuario por su ID."""
        if not self.db:
            return None
        try:
            doc = self.db.collection("users").document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception:
            return None

    def get_login_stats(self) -> dict:
        """Estadísticas de acceso para el admin."""
        if not self.db:
            return {"total_active_users": 0, "by_role": {}, "recent_logins": [], "failed_logins_today": 0}
        try:
            users = self.db.collection("users").where("active", "==", True).get()
            total = 0
            by_role = {}
            recent = []
            for u in users:
                data = u.to_dict()
                total += 1
                role = data.get("role", "alumno")
                by_role[role] = by_role.get(role, 0) + 1
                if data.get("last_login"):
                    recent.append({
                        "name":       data.get("name", ""),
                        "role":       role,
                        "last_login": data.get("last_login", ""),
                    })

            recent.sort(key=lambda x: x["last_login"], reverse=True)

            # Intentos fallidos hoy
            today = datetime.now().strftime("%Y-%m-%d")
            failed_logs = self.db.collection("login_log").where("success", "==", False).get()
            failed_today = sum(1 for f in failed_logs if f.to_dict().get("timestamp", "").startswith(today))

            return {
                "total_active_users":  total,
                "by_role":             by_role,
                "recent_logins":       recent[:10],
                "failed_logins_today": failed_today,
            }
        except Exception:
            return {"total_active_users": 0, "by_role": {}, "recent_logins": [], "failed_logins_today": 0}

    def close(self):
        pass


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
    st.session_state.pop("auth_token", None)
    st.session_state.pop("current_user", None)
    return False


def get_current_user() -> Optional[dict]:
    """Retorna el usuario actual de la sesión."""
    return st.session_state.get("current_user")


def require_auth(allowed_roles: list = None):
    """Guard para páginas protegidas."""
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
    for key in ["auth_token", "current_user", "auth_manager",
                "orchestrator_alumno", "orchestrator_profesor", "orchestrator_cfo",
                "messages_alumno", "messages_profesor", "messages_cfo"]:
        st.session_state.pop(key, None)