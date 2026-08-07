"""
CFO Agent IA - Panel de Administración
Gestión de usuarios, roles y monitoreo de accesos
"""
import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.auth_manager import init_auth, require_auth, logout_user, ROLES, SECTORS
from i18n.translations import t

st.set_page_config(
    page_title="CFO Agent IA — Admin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.admin-card { background:linear-gradient(135deg,#7D3C98,#9B59B6); border-radius:12px;
              padding:18px; color:white; text-align:center; margin:4px; }
.admin-value{ font-size:32px; font-weight:bold; }
.admin-label{ font-size:13px; opacity:0.85; margin-top:4px; }
.user-active  { background:#F0FFF4; border-left:4px solid #00AA44; padding:8px; border-radius:6px; margin:4px 0; }
.user-inactive{ background:#FFF0F0; border-left:4px solid #FF4444; padding:8px; border-radius:6px; margin:4px 0; }
</style>
""", unsafe_allow_html=True)

# ── AUTENTICACIÓN ─────────────────────────────────────────────────────────────
user = require_auth(allowed_roles=["admin"])
lang = st.session_state.get("lang", "es")
auth = init_auth()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/settings.png", width=60)
    st.title("⚙️ Administración")
    st.caption(f"{'Sesión' if lang == 'es' else 'Session'}: **{user['name']}**")
    st.divider()

    if st.button("🚪 Cerrar Sesión" if lang == "es" else "🚪 Sign Out",
                 use_container_width=True, type="secondary"):
        logout_user()
        st.switch_page("login.py")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("⚙️ Panel de Administración — CFO Agent IA")
st.caption(f"{'Gestión de usuarios, roles y monitoreo de accesos' if lang == 'es' else 'User management, roles and access monitoring'}")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
stats = auth.get_login_stats()
col1, col2, col3, col4, col5 = st.columns(5)
kpis = [
    ("👥", stats["total_active_users"], "Usuarios Activos" if lang == "es" else "Active Users"),
    ("🎓", stats["by_role"].get("alumno", 0),   "Alumnos" if lang == "es" else "Students"),
    ("👨‍🏫", stats["by_role"].get("profesor", 0), "Profesores" if lang == "es" else "Teachers"),
    ("💼", stats["by_role"].get("cfo", 0),       "CFO / Gerentes" if lang == "es" else "CFO / Managers"),
    ("🔴", stats["failed_logins_today"],          "Intentos fallidos hoy" if lang == "es" else "Failed logins today"),
]
for col, (icon, val, label) in zip([col1, col2, col3, col4, col5], kpis):
    with col:
        st.markdown(f"""
        <div class="admin-card">
            <div style="font-size:28px">{icon}</div>
            <div class="admin-value">{val}</div>
            <div class="admin-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_users, tab_create, tab_monitor = st.tabs([
    "👥 Gestión de Usuarios" if lang == "es" else "👥 User Management",
    "➕ Crear Usuario" if lang == "es" else "➕ Create User",
    "📊 Monitoreo de Accesos" if lang == "es" else "📊 Access Monitoring",
])

# ── TAB 1: GESTIÓN DE USUARIOS ────────────────────────────────────────────────
with tab_users:
    st.subheader("👥 Lista de Usuarios" if lang == "es" else "👥 User List")

    users = auth.get_all_users()
    if users:
        df = pd.DataFrame(users)

        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_role = st.selectbox(
                "Filtrar por rol:" if lang == "es" else "Filter by role:",
                ["Todos / All"] + list(ROLES.keys()),
            )
        with col_f2:
            filter_active = st.selectbox(
                "Estado:" if lang == "es" else "Status:",
                ["Todos / All", "Activos / Active", "Inactivos / Inactive"],
            )
        with col_f3:
            search = st.text_input("🔍 Buscar:" if lang == "es" else "🔍 Search:", placeholder="Nombre o email...")

        # Aplicar filtros
        filtered = df.copy()
        if filter_role != "Todos / All":
            filtered = filtered[filtered["role"] == filter_role]
        if "Activos" in filter_active or "Active" in filter_active:
            filtered = filtered[filtered["active"] == 1]
        elif "Inactivos" in filter_active or "Inactive" in filter_active:
            filtered = filtered[filtered["active"] == 0]
        if search:
            mask = (filtered["name"].str.contains(search, case=False, na=False) |
                    filtered["email"].str.contains(search, case=False, na=False))
            filtered = filtered[mask]

        # Mostrar tabla
        display_cols = ["name", "email", "role", "sector", "active", "last_login"]
        col_labels = {
            "name": "Nombre" if lang == "es" else "Name",
            "email": "Email",
            "role": "Rol" if lang == "es" else "Role",
            "sector": "Sector",
            "active": "Activo" if lang == "es" else "Active",
            "last_login": "Último acceso" if lang == "es" else "Last login",
        }
        show_df = filtered[[c for c in display_cols if c in filtered.columns]].rename(columns=col_labels)
        st.dataframe(show_df, use_container_width=True, height=300)

        st.divider()
        st.subheader("✏️ Editar Usuario" if lang == "es" else "✏️ Edit User")

        user_options = {f"{u['name']} ({u['email']})": u["id"] for u in users if u["id"] != user["id"]}
        selected_label = st.selectbox(
            "Seleccionar usuario:" if lang == "es" else "Select user:",
            list(user_options.keys()),
        )

        if selected_label:
            selected_id = user_options[selected_label]
            selected_user = auth.get_user_by_id(selected_id)

            with st.form("edit_user_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_name = st.text_input("Nombre:" if lang == "es" else "Name:", value=selected_user["name"])
                    new_role = st.selectbox(
                        "Rol:" if lang == "es" else "Role:",
                        list(ROLES.keys()),
                        index=list(ROLES.keys()).index(selected_user["role"]) if selected_user["role"] in ROLES else 0,
                        format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x][f'label_{lang}']}",
                    )
                with col_e2:
                    new_sector = st.selectbox(
                        "Sector:",
                        SECTORS,
                        index=SECTORS.index(selected_user["sector"]) if selected_user["sector"] in SECTORS else 0,
                    )
                    new_active = st.checkbox(
                        "Usuario activo" if lang == "es" else "Active user",
                        value=bool(selected_user["active"])
                    )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    save_btn = st.form_submit_button(
                        "💾 Guardar cambios" if lang == "es" else "💾 Save changes",
                        type="primary", use_container_width=True
                    )
                with col_btn2:
                    reset_btn = st.form_submit_button(
                        "🔑 Resetear contraseña" if lang == "es" else "🔑 Reset password",
                        use_container_width=True
                    )

            if save_btn:
                result = auth.update_user(
                    selected_id,
                    name=new_name,
                    role=new_role,
                    sector=new_sector,
                    active=int(new_active),
                )
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(result["message"])

            if reset_btn:
                result = auth.reset_password(selected_id)
                if result["success"]:
                    st.success(f"✅ Nueva contraseña temporal: **`{result['new_password']}`**")
                    st.info("📧 Comparte esta contraseña con el usuario de forma segura." if lang == "es"
                            else "📧 Share this password with the user securely.")
    else:
        st.info("No hay usuarios registrados aún." if lang == "es" else "No users registered yet.")

# ── TAB 2: CREAR USUARIO ──────────────────────────────────────────────────────
with tab_create:
    st.subheader("➕ Crear Nuevo Usuario" if lang == "es" else "➕ Create New User")

    # Creación individual
    with st.expander("👤 Crear usuario individual" if lang == "es" else "👤 Create individual user", expanded=True):
        with st.form("create_user_form"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                new_email  = st.text_input("📧 Email:", placeholder="alumno@empresa.com")
                new_name   = st.text_input("👤 Nombre completo:" if lang == "es" else "👤 Full name:", placeholder="Juan Pérez")
                new_role   = st.selectbox(
                    "🎭 Rol:" if lang == "es" else "🎭 Role:",
                    list(ROLES.keys()),
                    format_func=lambda x: f"{ROLES[x]['icon']} {ROLES[x][f'label_{lang}']}",
                )
            with col_c2:
                new_sector = st.selectbox("🏭 Sector:", SECTORS)
                set_password = st.checkbox(
                    "Establecer contraseña manual" if lang == "es" else "Set manual password"
                )
                manual_pwd = ""
                if set_password:
                    manual_pwd = st.text_input(
                        "🔑 Contraseña:" if lang == "es" else "🔑 Password:",
                        type="password",
                        help="Mínimo 8 caracteres" if lang == "es" else "Minimum 8 characters"
                    )

            create_btn = st.form_submit_button(
                "➕ Crear Usuario" if lang == "es" else "➕ Create User",
                type="primary", use_container_width=True
            )

        if create_btn:
            if not new_email or not new_name:
                st.error("Email y nombre son obligatorios." if lang == "es" else "Email and name are required.")
            else:
                result = auth.create_user(
                    email=new_email,
                    name=new_name,
                    role=new_role,
                    sector=new_sector,
                    password=manual_pwd if set_password and manual_pwd else None,
                    created_by=user["email"],
                )
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.info(f"""
                    📋 **Credenciales del nuevo usuario:**
                    - **Email:** `{result['email']}`
                    - **Contraseña temporal:** `{result['temp_password']}`
                    """)
                else:
                    st.error(f"❌ {result['message']}")

    # Creación masiva
    with st.expander("📋 Crear múltiples usuarios (carga masiva)" if lang == "es" else "📋 Create multiple users (bulk upload)"):
        st.markdown("""
        **Formato CSV requerido:**
        ```
        email,name,role,sector
        alumno1@empresa.com,Juan Pérez,alumno,mining
        alumno2@empresa.com,María García,alumno,mining
        profesor@empresa.com,Dr. López,profesor,mining
        ```
        """)
        uploaded_csv = st.file_uploader(
            "📁 Subir CSV:" if lang == "es" else "📁 Upload CSV:",
            type=["csv"]
        )
        if uploaded_csv:
            import io
            df_upload = pd.read_csv(io.StringIO(uploaded_csv.read().decode("utf-8")))
            st.dataframe(df_upload, use_container_width=True)

            if st.button("🚀 Crear todos los usuarios" if lang == "es" else "🚀 Create all users",
                         type="primary"):
                results = []
                for _, row in df_upload.iterrows():
                    r = auth.create_user(
                        email=str(row.get("email", "")),
                        name=str(row.get("name", "")),
                        role=str(row.get("role", "alumno")),
                        sector=str(row.get("sector", "mining")),
                        created_by=user["email"],
                    )
                    results.append({
                        "Email": row.get("email", ""),
                        "Resultado": "✅ Creado" if r["success"] else f"❌ {r['message']}",
                        "Contraseña": r.get("temp_password", "—"),
                    })
                st.dataframe(pd.DataFrame(results), use_container_width=True)

                # Exportar resultados
                csv_out = pd.DataFrame(results).to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Descargar resultados" if lang == "es" else "📥 Download results",
                    data=csv_out,
                    file_name=f"usuarios_creados_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

# ── TAB 3: MONITOREO ──────────────────────────────────────────────────────────
with tab_monitor:
    st.subheader("📊 Monitoreo de Accesos" if lang == "es" else "📊 Access Monitoring")

    # Últimos accesos
    st.markdown("**🕐 Últimos accesos:**" if lang == "es" else "**🕐 Recent logins:**")
    recent = stats.get("recent_logins", [])
    if recent:
        df_recent = pd.DataFrame(recent)
        df_recent.columns = (
            ["Nombre", "Rol", "Último acceso"] if lang == "es"
            else ["Name", "Role", "Last login"]
        )
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("Sin accesos registrados aún." if lang == "es" else "No logins recorded yet.")

    st.divider()

    # Distribución por rol
    st.markdown("**👥 Distribución por rol:**" if lang == "es" else "**👥 Distribution by role:**")
    by_role = stats.get("by_role", {})
    if by_role:
        col_r = st.columns(len(by_role))
        for i, (role_key, count) in enumerate(by_role.items()):
            with col_r[i]:
                role_info = ROLES.get(role_key, {})
                st.metric(
                    f"{role_info.get('icon', '')} {role_info.get(f'label_{lang}', role_key)}",
                    count
                )

    if stats["failed_logins_today"] > 0:
        st.warning(
            f"⚠️ {stats['failed_logins_today']} intento(s) de acceso fallido(s) hoy."
            if lang == "es" else
            f"⚠️ {stats['failed_logins_today']} failed login attempt(s) today."
        )
