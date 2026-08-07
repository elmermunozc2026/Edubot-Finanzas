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
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
body { background: linear-gradient(135deg, #1F4E79, #2E75B6); min-height: 100vh; }
</style>
""", unsafe_allow_html=True)

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
    if role == "admin":
        st.switch_page("pages/0_Admin.py")
    elif role == "alumno":
        st.switch_page("pages/1_Alumno.py")
    elif role == "profesor":
        st.switch_page("pages/2_Profesor.py")
    elif role == "cfo":
        st.switch_page("pages/3_CFO_Asistente.py")
    else:
        st.switch_page("pages/1_Alumno.py")
    st.stop()

# ── FORMULARIO DE LOGIN ───────────────────────────────────────────────────────
_, col_center, _ = st.columns([1, 3, 1])
with col_center:
    st.markdown(f"""
    <div style="background:white;border-radius:20px;padding:40px 32px;
                box-shadow:0 8px 32px rgba(31,78,121,0.15);max-width:420px;margin:0 auto">
        <div style="text-align:center;font-size:64px">🏦</div>
        <div style="text-align:center;font-size:28px;font-weight:900;color:#1F4E79">{T['title']}</div>
        <div style="text-align:center;font-size:14px;color:#7F7F7F;margin-bottom:28px">{T['sub']}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email    = st.text_input(T["email"],    placeholder="usuario@empresa.com")
        password = st.text_input(T["password"], type="password", placeholder="••••••••")
        submitted = st.form_submit_button(
            T["btn_login"], type="primary", use_container_width=True
        )

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

                import time
                time.sleep(1)

                if role == "admin":
                    st.switch_page("pages/0_Admin.py")
                elif role == "alumno":
                    st.switch_page("pages/1_Alumno.py")
                elif role == "profesor":
                    st.switch_page("pages/2_Profesor.py")
                elif role == "cfo":
                    st.switch_page("pages/3_CFO_Asistente.py")
                else:
                    st.switch_page("pages/1_Alumno.py")
            else:
                st.error(f"❌ {result['message']}")

    st.caption(T["forgot"])
    st.divider()

    # ── ROLES DISPONIBLES ─────────────────────────────────────────────────────
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
                        padding:8px;text-align:center;font-size:12px;
                        color:{color};font-weight:bold">
                {role_data['icon']}<br>{label}
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.caption(
        "CFO Agent IA © 2026 | Sesión segura de 8 horas" if lang == "es"
        else "CFO Agent IA © 2026 | Secure 8-hour session"
    )