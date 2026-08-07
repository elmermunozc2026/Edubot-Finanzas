"""
CFO Agent IA - Página de Login
Punto de entrada con autenticación y redirección por rol
"""
import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.auth_manager import init_auth, is_authenticated, get_current_user, ROLES

st.set_page_config(
    page_title="CFO Agent IA — Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Ocultar sidebar en login */
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.login-container {
    max-width: 420px; margin: 0 auto; padding: 40px 32px;
    background: white; border-radius: 20px;
    box-shadow: 0 8px 32px rgba(31,78,121,0.15);
}
.login-logo    { text-align: center; font-size: 64px; margin-bottom: 8px; }
.login-title   { text-align: center; font-size: 28px; font-weight: 900;
                 color: #1F4E79; margin-bottom: 4px; }
.login-sub     { text-align: center; font-size: 14px; color: #7F7F7F;
                 margin-bottom: 28px; }
.role-badge    { display: inline-block; padding: 4px 12px; border-radius: 20px;
                 font-size: 13px; font-weight: bold; margin: 2px; }
.lang-bar      { background: #EEF2F7; border-radius: 10px; padding: 8px 12px;
                 margin-bottom: 20px; text-align: center; }
body { background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 50%, #1F4E79 100%);
       min-height: 100vh; }
</style>
""", unsafe_allow_html=True)

# ── IDIOMA ────────────────────────────────────────────────────────────────────
lang = st.session_state.get("lang", "es")

TEXTS = {
    "es": {
        "title": "CFO Agent IA",
        "sub": "Plataforma de Inteligencia Financiera",
        "lang_label": "🌐 Idioma:",
        "email": "📧 Correo electrónico",
        "password": "🔑 Contraseña",
        "btn_login": "🚀 Ingresar",
        "forgot": "¿Olvidaste tu contraseña? Contacta al administrador.",
        "error_empty": "Por favor ingresa tu correo y contraseña.",
        "logging_in": "Verificando credenciales...",
        "welcome": "Bienvenido/a",
        "redirecting": "Redirigiendo a tu módulo...",
        "roles_title": "Acceso por perfil:",
    },
    "en": {
        "title": "CFO Agent IA",
        "sub": "Financial Intelligence Platform",
        "lang_label": "🌐 Language:",
        "email": "📧 Email address",
        "password": "🔑 Password",
        "btn_login": "🚀 Sign In",
        "forgot": "Forgot your password? Contact the administrator.",
        "error_empty": "Please enter your email and password.",
        "logging_in": "Verifying credentials...",
        "welcome": "Welcome",
        "redirecting": "Redirecting to your module...",
        "roles_title": "Access by profile:",
    },
}
T = TEXTS[lang]

# ── SELECTOR DE IDIOMA ────────────────────────────────────────────────────────
col_lang = st.columns([1, 2, 1])[1]
with col_lang:
    idioma = st.radio(
        T["lang_label"],
        ["🇪🇸 Español", "🇺🇸 English"],
        horizontal=True,
        key="idioma_login",
        index=0 if lang == "es" else 1,
        label_visibility="collapsed",
    )
    new_lang = "en" if "English" in idioma else "es"
    if new_lang != lang:
        st.session_state["lang"] = new_lang
        st.rerun()

# ── SI YA ESTÁ AUTENTICADO → REDIRIGIR ───────────────────────────────────────
if is_authenticated():
    user = get_current_user()
    role = user.get("role", "alumno")
    page_map = {
        "admin":    "app.py",
        "alumno":   "pages/1_Alumno.py",
        "profesor": "pages/2_Profesor.py",
        "cfo":      "pages/3_CFO_Asistente.py",
    }
    st.switch_page(page_map.get(role, "app.py"))
    st.stop()

# ── FORMULARIO DE LOGIN ───────────────────────────────────────────────────────
_, col_center, _ = st.columns([1, 3, 1])
with col_center:
    st.markdown(f"""
    <div class="login-container">
        <div class="login-logo">🏦</div>
        <div class="login-title">{T['title']}</div>
        <div class="login-sub">{T['sub']}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email    = st.text_input(T["email"],    placeholder="usuario@empresa.com")
        password = st.text_input(T["password"], type="password", placeholder="••••••••")
        submitted = st.form_submit_button(T["btn_login"], type="primary", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error(T["error_empty"])
        else:
            with st.spinner(T["logging_in"]):
                auth = init_auth()
                result = auth.login(email, password)

            if result["success"]:
                st.session_state["auth_token"]   = result["token"]
                st.session_state["current_user"] = result["user"]
                user = result["user"]
                role = user.get("role", "alumno")

                st.success(f"✅ {T['welcome']}, **{user['name']}**! {T['redirecting']}")

                page_map = {
                    "admin":    "app.py",
                    "alumno":   "pages/1_Alumno.py",
                    "profesor": "pages/2_Profesor.py",
                    "cfo":      "pages/3_CFO_Asistente.py",
                }
                import time; time.sleep(1)
                st.switch_page(page_map.get(role, "app.py"))
            else:
                st.error(f"❌ {result['message']}")

    st.caption(T["forgot"])
    st.divider()

    # Mostrar roles disponibles
    st.markdown(f"**{T['roles_title']}**")
    role_colors = {
        "admin":    "#7D3C98",
        "alumno":   "#1F4E79",
        "profesor": "#1E8449",
        "cfo":      "#B7950B",
    }
    cols = st.columns(4)
    for i, (role_key, role_data) in enumerate(ROLES.items()):
        with cols[i]:
            label = role_data[f"label_{lang}"]
            color = role_colors[role_key]
            st.markdown(f"""
            <div style="background:{color}22;border:1px solid {color};border-radius:8px;
                        padding:8px;text-align:center;font-size:12px;color:{color};font-weight:bold">
                {role_data['icon']}<br>{label}
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.caption("CFO Agent IA © 2026 | Acceso seguro con sesión de 8 horas" if lang == "es"
               else "CFO Agent IA © 2026 | Secure access with 8-hour session")
