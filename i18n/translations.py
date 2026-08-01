"""
CFO Agent IA - Sistema de Internacionalización (i18n)
Soporte bilingüe: Español (es) / English (en)
Uso: from i18n.translations import t, SECTORS, MODULES
"""

# ─────────────────────────────────────────────────────────────────────────────
# DICCIONARIO PRINCIPAL DE TEXTOS
# ─────────────────────────────────────────────────────────────────────────────

TEXTS = {
    # ── GENERAL / NAVEGACIÓN ─────────────────────────────────────────────────
    "app_title": {
        "es": "CFO Agent IA",
        "en": "CFO Agent IA",
    },
    "app_subtitle": {
        "es": "De Edubot a Agente IA Empresarial — Finanzas & Contabilidad Multi-Sector",
        "en": "From Edubot to Enterprise AI Agent — Finance & Accounting Multi-Sector",
    },
    "language_selector": {
        "es": "🌐 Idioma / Language:",
        "en": "🌐 Language / Idioma:",
    },
    "agente_activo": {
        "es": "🟢 Agente Activo",
        "en": "🟢 Agent Active",
    },
    "nueva_sesion": {
        "es": "🔄 Nueva Sesión",
        "en": "🔄 New Session",
    },
    "guardar_config": {
        "es": "💾 Guardar Configuración",
        "en": "💾 Save Configuration",
    },
    "config_guardada": {
        "es": "✅ Configuración guardada exitosamente.",
        "en": "✅ Configuration saved successfully.",
    },
    "error_api": {
        "es": "⚠️ API Key no configurada. Agrega GEMINI_API_KEY en los secretos de Streamlit.",
        "en": "⚠️ API Key not configured. Add GEMINI_API_KEY to Streamlit secrets.",
    },
    "analizando": {
        "es": "El CFO Agent está analizando...",
        "en": "CFO Agent is analyzing...",
    },
    "herramientas_usadas": {
        "es": "🔧 Herramientas usadas",
        "en": "🔧 Tools used",
    },
    "exportar_csv": {
        "es": "📥 Exportar CSV",
        "en": "📥 Export CSV",
    },
    "descargar_reporte": {
        "es": "📥 Descargar Reporte (TXT)",
        "en": "📥 Download Report (TXT)",
    },

    # ── HOME PAGE ────────────────────────────────────────────────────────────
    "home_stats_agentes": {
        "es": "Agentes IA",
        "en": "AI Agents",
    },
    "home_stats_herramientas": {
        "es": "Herramientas",
        "en": "Tools",
    },
    "home_stats_sectores": {
        "es": "Sectores",
        "en": "Sectors",
    },
    "home_stats_modulos": {
        "es": "Módulos CFO",
        "en": "CFO Modules",
    },
    "home_stats_alumnos": {
        "es": "Alumnos",
        "en": "Students",
    },
    "home_modulos_titulo": {
        "es": "🚀 Módulos del Sistema",
        "en": "🚀 System Modules",
    },
    "home_mod1_titulo": {
        "es": "Módulo Educativo",
        "en": "Educational Module",
    },
    "home_mod1_desc": {
        "es": "Tutor socrático adaptativo para clases de Finanzas y Contabilidad. Memoria por alumno, evaluación automática y quizzes adaptativos.",
        "en": "Adaptive Socratic tutor for Finance and Accounting classes. Per-student memory, automatic evaluation and adaptive quizzes.",
    },
    "home_mod1_link": {
        "es": "→ Ir al Módulo Alumno",
        "en": "→ Go to Student Module",
    },
    "home_mod2_titulo": {
        "es": "Dashboard Profesor",
        "en": "Teacher Dashboard",
    },
    "home_mod2_desc": {
        "es": "Panel de control con métricas de los 20 alumnos, alertas automáticas, ranking y exportación de reportes.",
        "en": "Control panel with metrics for 20 students, automatic alerts, ranking and report export.",
    },
    "home_mod2_link": {
        "es": "→ Ir al Dashboard Profesor",
        "en": "→ Go to Teacher Dashboard",
    },
    "home_mod3_titulo": {
        "es": "Asistente CFO",
        "en": "CFO Assistant",
    },
    "home_mod3_desc": {
        "es": "Asistente ejecutivo para el Director de Finanzas: análisis, presupuestos, tesorería, riesgos, impuestos y reporting.",
        "en": "Executive assistant for the CFO: analysis, budgets, treasury, risks, taxes and reporting.",
    },
    "home_mod3_link": {
        "es": "→ Ir al Asistente CFO",
        "en": "→ Go to CFO Assistant",
    },
    "home_capacidades_titulo": {
        "es": "🔧 Capacidades del Agente IA",
        "en": "🔧 AI Agent Capabilities",
    },
    "home_sectores_titulo": {
        "es": "🏭 Sectores Disponibles",
        "en": "🏭 Available Sectors",
    },
    "home_arquitectura_titulo": {
        "es": "📐 Arquitectura Técnica",
        "en": "📐 Technical Architecture",
    },
    "home_roadmap_titulo": {
        "es": "🗺️ Roadmap de Implementación",
        "en": "🗺️ Implementation Roadmap",
    },

    # ── PÁGINA ALUMNO ────────────────────────────────────────────────────────
    "alumno_titulo": {
        "es": "🎓 Tutor CFO — Módulo Educativo",
        "en": "🎓 CFO Tutor — Educational Module",
    },
    "alumno_caption": {
        "es": "Bienvenido/a",
        "en": "Welcome",
    },
    "alumno_nombre": {
        "es": "👤 Tu nombre:",
        "en": "👤 Your name:",
    },
    "alumno_nombre_placeholder": {
        "es": "Ej: María García",
        "en": "E.g.: Mary Smith",
    },
    "alumno_sector": {
        "es": "🏭 Sector de estudio:",
        "en": "🏭 Study sector:",
    },
    "alumno_promedio": {
        "es": "Promedio General",
        "en": "Overall Average",
    },
    "alumno_sesiones": {
        "es": "💬 Sesiones",
        "en": "💬 Sessions",
    },
    "alumno_nivel": {
        "es": "📚 Nivel",
        "en": "📚 Level",
    },
    "alumno_reforzar": {
        "es": "📌 Reforzar:",
        "en": "📌 Reinforce:",
    },
    "alumno_tab_chat": {
        "es": "💬 Chat con el Tutor",
        "en": "💬 Chat with Tutor",
    },
    "alumno_tab_progreso": {
        "es": "📊 Mi Progreso",
        "en": "📊 My Progress",
    },
    "alumno_tab_temas": {
        "es": "📚 Temas Disponibles",
        "en": "📚 Available Topics",
    },
    "alumno_chat_placeholder": {
        "es": "Escribe tu pregunta o respuesta aquí...",
        "en": "Type your question or answer here...",
    },
    "alumno_ingresa_nombre": {
        "es": "👆 Ingresa tu nombre en el panel izquierdo para comenzar la sesión.",
        "en": "👆 Enter your name in the left panel to start the session.",
    },
    "alumno_iniciando": {
        "es": "Iniciando sesión con el tutor...",
        "en": "Starting session with tutor...",
    },
    "alumno_nivel_basico": {
        "es": "🟡 Básico",
        "en": "🟡 Basic",
    },
    "alumno_nivel_intermedio": {
        "es": "🔵 Intermedio",
        "en": "🔵 Intermediate",
    },
    "alumno_nivel_avanzado": {
        "es": "🟢 Avanzado",
        "en": "🟢 Advanced",
    },
    "alumno_temas_refuerzo": {
        "es": "📌 Temas que necesitan refuerzo",
        "en": "📌 Topics that need reinforcement",
    },
    "alumno_desempeno_tema": {
        "es": "📈 Desempeño por Tema",
        "en": "📈 Performance by Topic",
    },
    "alumno_ingresa_nombre_progreso": {
        "es": "Ingresa tu nombre para ver tu progreso.",
        "en": "Enter your name to see your progress.",
    },
    "alumno_programa_titulo": {
        "es": "📚 Temas del Programa CFO Agent IA",
        "en": "📚 CFO Agent IA Program Topics",
    },
    "alumno_temas_reforzar_pedir": {
        "es": "Pide al tutor que te explique este tema",
        "en": "Ask the tutor to explain this topic",
    },

    # ── PÁGINA PROFESOR ──────────────────────────────────────────────────────
    "profesor_titulo": {
        "es": "👨‍🏫 Dashboard del Profesor — CFO Agent IA",
        "en": "👨‍🏫 Teacher Dashboard — CFO Agent IA",
    },
    "profesor_nombre": {
        "es": "👤 Nombre del Profesor:",
        "en": "👤 Teacher Name:",
    },
    "profesor_sector_clase": {
        "es": "🏭 Sector de la clase:",
        "en": "🏭 Class sector:",
    },
    "profesor_config_clase": {
        "es": "⚙️ Configuración de Clase",
        "en": "⚙️ Class Configuration",
    },
    "profesor_num_alumnos": {
        "es": "Número de alumnos:",
        "en": "Number of students:",
    },
    "profesor_umbral_riesgo": {
        "es": "Umbral de riesgo (promedio):",
        "en": "Risk threshold (average):",
    },
    "profesor_actualizar": {
        "es": "🔄 Actualizar Dashboard",
        "en": "🔄 Refresh Dashboard",
    },
    "profesor_kpi_activos": {
        "es": "Alumnos Activos",
        "en": "Active Students",
    },
    "profesor_kpi_promedio": {
        "es": "Promedio Clase",
        "en": "Class Average",
    },
    "profesor_kpi_riesgo": {
        "es": "🔴 En Riesgo",
        "en": "🔴 At Risk",
    },
    "profesor_kpi_destacados": {
        "es": "🟢 Destacados",
        "en": "🟢 Outstanding",
    },
    "profesor_kpi_aprobacion": {
        "es": "Tasa Aprobación",
        "en": "Pass Rate",
    },
    "profesor_tab_ranking": {
        "es": "📊 Ranking de Alumnos",
        "en": "📊 Student Ranking",
    },
    "profesor_tab_alertas": {
        "es": "🚨 Alertas y Acciones",
        "en": "🚨 Alerts & Actions",
    },
    "profesor_tab_chat": {
        "es": "🤖 Asistente del Profesor",
        "en": "🤖 Teacher Assistant",
    },
    "profesor_tab_config": {
        "es": "⚙️ Configurar Clase",
        "en": "⚙️ Configure Class",
    },
    "profesor_ranking_titulo": {
        "es": "📊 Ranking Completo de la Clase",
        "en": "📊 Complete Class Ranking",
    },
    "profesor_alertas_titulo": {
        "es": "🚨 Alertas que Requieren Atención",
        "en": "🚨 Alerts Requiring Attention",
    },
    "profesor_sin_riesgo": {
        "es": "✅ No hay alumnos en situación de riesgo actualmente.",
        "en": "✅ No students currently at risk.",
    },
    "profesor_destacados_titulo": {
        "es": "🏆 Alumnos Destacados",
        "en": "🏆 Outstanding Students",
    },
    "profesor_asistente_titulo": {
        "es": "🤖 Asistente IA del Profesor",
        "en": "🤖 AI Teacher Assistant",
    },
    "profesor_asistente_caption": {
        "es": "Consulta al agente sobre la gestión de tu clase, estrategias pedagógicas o análisis del grupo.",
        "en": "Ask the agent about class management, pedagogical strategies or group analysis.",
    },
    "profesor_chat_placeholder": {
        "es": "Consulta al asistente del profesor...",
        "en": "Ask the teacher assistant...",
    },
    "profesor_quick1": {
        "es": "📊 Resumen de la clase",
        "en": "📊 Class summary",
    },
    "profesor_quick2": {
        "es": "🎯 Sugerir próxima clase",
        "en": "🎯 Suggest next class",
    },
    "profesor_quick3": {
        "es": "📝 Generar quiz grupal",
        "en": "📝 Generate group quiz",
    },
    "profesor_quick1_query": {
        "es": "Dame un resumen completo del estado actual de la clase con métricas clave.",
        "en": "Give me a complete summary of the current class status with key metrics.",
    },
    "profesor_quick2_query": {
        "es": "¿Qué tema debería enseñar en la próxima clase basándote en las brechas detectadas?",
        "en": "What topic should I teach in the next class based on detected gaps?",
    },
    "profesor_quick3_query": {
        "es": "Genera un quiz de 5 preguntas de nivel intermedio sobre ratios financieros para toda la clase.",
        "en": "Generate a 5-question intermediate-level quiz on financial ratios for the whole class.",
    },
    "profesor_config_titulo": {
        "es": "⚙️ Configuración de la Clase",
        "en": "⚙️ Class Configuration",
    },
    "profesor_temas_programa": {
        "es": "📚 Temas del Programa",
        "en": "📚 Program Topics",
    },
    "profesor_temas_habilitados": {
        "es": "Temas habilitados:",
        "en": "Enabled topics:",
    },
    "profesor_niveles_titulo": {
        "es": "🎯 Niveles de Dificultad",
        "en": "🎯 Difficulty Levels",
    },
    "profesor_niveles_disponibles": {
        "es": "Niveles disponibles:",
        "en": "Available levels:",
    },
    "profesor_params_eval": {
        "es": "📊 Parámetros de Evaluación",
        "en": "📊 Evaluation Parameters",
    },
    "profesor_nota_aprobacion": {
        "es": "Nota mínima de aprobación:",
        "en": "Minimum passing grade:",
    },
    "profesor_preguntas_quiz": {
        "es": "Preguntas por quiz:",
        "en": "Questions per quiz:",
    },
    "profesor_tiempo_pregunta": {
        "es": "Tiempo por pregunta (min):",
        "en": "Time per question (min):",
    },
    "profesor_alertas_auto": {
        "es": "🔔 Alertas Automáticas",
        "en": "🔔 Automatic Alerts",
    },
    "profesor_alerta_inactividad": {
        "es": "Alertar si inactivo (días):",
        "en": "Alert if inactive (days):",
    },
    "profesor_alerta_promedio": {
        "es": "Alertar si promedio < :",
        "en": "Alert if average < :",
    },
    "profesor_sin_datos": {
        "es": "📭 Aún no hay datos de alumnos. Los datos aparecerán cuando los alumnos comiencen a usar el sistema.",
        "en": "📭 No student data yet. Data will appear when students start using the system.",
    },
    "profesor_vista_demo": {
        "es": "👁️ Vista Previa (Datos Demo)",
        "en": "👁️ Preview (Demo Data)",
    },
    "profesor_acciones_sugeridas": {
        "es": "Acciones sugeridas:",
        "en": "Suggested actions:",
    },
    "profesor_accion1": {
        "es": "📞 Contactar al alumno para sesión de refuerzo",
        "en": "📞 Contact student for reinforcement session",
    },
    "profesor_accion2": {
        "es": "📚 Asignar material adicional sobre temas débiles",
        "en": "📚 Assign additional material on weak topics",
    },
    "profesor_accion3": {
        "es": "🎯 Programar evaluación de recuperación",
        "en": "🎯 Schedule recovery evaluation",
    },

    # ── PÁGINA CFO ASISTENTE ─────────────────────────────────────────────────
    "cfo_titulo": {
        "es": "💼 Asistente Ejecutivo CFO",
        "en": "💼 CFO Executive Assistant",
    },
    "cfo_nombre": {
        "es": "👤 Nombre del CFO/Gerente:",
        "en": "👤 CFO/Manager Name:",
    },
    "cfo_empresa": {
        "es": "🏢 Empresa:",
        "en": "🏢 Company:",
    },
    "cfo_sector": {
        "es": "🏭 Sector:",
        "en": "🏭 Sector:",
    },
    "cfo_modulos": {
        "es": "📋 Módulos CFO",
        "en": "📋 CFO Modules",
    },
    "cfo_nueva_sesion": {
        "es": "🔄 Nueva Sesión Ejecutiva",
        "en": "🔄 New Executive Session",
    },
    "cfo_chat_titulo": {
        "es": "🤖 Chat Ejecutivo CFO",
        "en": "🤖 CFO Executive Chat",
    },
    "cfo_chat_placeholder": {
        "es": "Consulta ejecutiva...",
        "en": "Executive query...",
    },
    "cfo_iniciando": {
        "es": "Iniciando sesión ejecutiva...",
        "en": "Starting executive session...",
    },
    "cfo_calculando": {
        "es": "Calculando...",
        "en": "Calculating...",
    },
    "cfo_proyectando": {
        "es": "Proyectando...",
        "en": "Projecting...",
    },
    "cfo_evaluando": {
        "es": "Evaluando proyecto...",
        "en": "Evaluating project...",
    },
    "cfo_generando_reporte": {
        "es": "Generando reporte ejecutivo...",
        "en": "Generating executive report...",
    },
    "cfo_quick_ratios": {
        "es": "📊 Ratios del mes",
        "en": "📊 Monthly ratios",
    },
    "cfo_quick_caja": {
        "es": "💰 Posición de caja",
        "en": "💰 Cash position",
    },
    "cfo_quick_riesgos": {
        "es": "⚠️ Matriz de riesgos",
        "en": "⚠️ Risk matrix",
    },
    "cfo_quick_sunat": {
        "es": "🧾 Calendario SUNAT",
        "en": "🧾 Tax calendar",
    },
    "cfo_analisis_titulo": {
        "es": "📊 Análisis Financiero",
        "en": "📊 Financial Analysis",
    },
    "cfo_analisis_caption": {
        "es": "Ingresa los datos financieros para análisis automático de ratios y KPIs.",
        "en": "Enter financial data for automatic ratio and KPI analysis.",
    },
    "cfo_balance_titulo": {
        "es": "💰 Datos del Balance General",
        "en": "💰 Balance Sheet Data",
    },
    "cfo_eerr_titulo": {
        "es": "📈 Datos del Estado de Resultados",
        "en": "📈 Income Statement Data",
    },
    "cfo_calcular_ratios": {
        "es": "🔍 Calcular Ratios y KPIs",
        "en": "🔍 Calculate Ratios & KPIs",
    },
    "cfo_analisis_ejecutivo": {
        "es": "### 📊 Análisis Ejecutivo de Ratios",
        "en": "### 📊 Executive Ratio Analysis",
    },
    "cfo_planeamiento_titulo": {
        "es": "📈 Planeamiento Financiero",
        "en": "📈 Financial Planning",
    },
    "cfo_tab_presupuesto": {
        "es": "💰 Presupuesto",
        "en": "💰 Budget",
    },
    "cfo_tab_forecast": {
        "es": "🔮 Forecast",
        "en": "🔮 Forecast",
    },
    "cfo_tab_capex": {
        "es": "🏗️ CAPEX",
        "en": "🏗️ CAPEX",
    },
    "cfo_construir_presupuesto": {
        "es": "📊 Construir Presupuesto",
        "en": "📊 Build Budget",
    },
    "cfo_proyectar_forecast": {
        "es": "🔮 Proyectar Forecast",
        "en": "🔮 Project Forecast",
    },
    "cfo_evaluar_capex": {
        "es": "🏗️ Evaluar CAPEX",
        "en": "🏗️ Evaluate CAPEX",
    },
    "cfo_tesoreria_titulo": {
        "es": "🏦 Gestión de Tesorería y Bancos",
        "en": "🏦 Treasury & Banking Management",
    },
    "cfo_tab_caja": {
        "es": "💰 Posición de Caja",
        "en": "💰 Cash Position",
    },
    "cfo_tab_bancos": {
        "es": "🏦 Líneas Bancarias",
        "en": "🏦 Bank Lines",
    },
    "cfo_tab_wc": {
        "es": "🔄 Capital de Trabajo",
        "en": "🔄 Working Capital",
    },
    "cfo_calcular_posicion": {
        "es": "💰 Calcular Posición",
        "en": "💰 Calculate Position",
    },
    "cfo_analizar_linea": {
        "es": "🏦 Analizar Línea Bancaria",
        "en": "🏦 Analyze Bank Line",
    },
    "cfo_optimizar_wc": {
        "es": "🔄 Optimizar Capital de Trabajo",
        "en": "🔄 Optimize Working Capital",
    },
    "cfo_riesgos_titulo": {
        "es": "⚠️ Gestión de Riesgos",
        "en": "⚠️ Risk Management",
    },
    "cfo_tab_matriz": {
        "es": "📋 Matriz de Riesgos",
        "en": "📋 Risk Matrix",
    },
    "cfo_tab_riesgo": {
        "es": "🎯 Evaluar Riesgo",
        "en": "🎯 Assess Risk",
    },
    "cfo_tab_var": {
        "es": "📉 Value at Risk",
        "en": "📉 Value at Risk",
    },
    "cfo_cargar_matriz": {
        "es": "📋 Cargar Matriz de Riesgos del Sector",
        "en": "📋 Load Sector Risk Matrix",
    },
    "cfo_evaluar_riesgo_btn": {
        "es": "⚠️ Evaluar Riesgo",
        "en": "⚠️ Assess Risk",
    },
    "cfo_calcular_var": {
        "es": "📉 Calcular VaR",
        "en": "📉 Calculate VaR",
    },
    "cfo_impuestos_titulo": {
        "es": "🧾 Gestión Tributaria — Perú",
        "en": "🧾 Tax Management — Peru",
    },
    "cfo_tab_ir": {
        "es": "💰 Impuesto a la Renta",
        "en": "💰 Income Tax",
    },
    "cfo_tab_igv": {
        "es": "🧾 Posición IGV",
        "en": "🧾 VAT Position",
    },
    "cfo_tab_calendario": {
        "es": "📅 Calendario SUNAT",
        "en": "📅 Tax Calendar",
    },
    "cfo_calcular_ir": {
        "es": "💰 Calcular IR",
        "en": "💰 Calculate Income Tax",
    },
    "cfo_calcular_igv": {
        "es": "🧾 Calcular Posición IGV",
        "en": "🧾 Calculate VAT Position",
    },
    "cfo_ver_calendario": {
        "es": "📅 Ver Calendario Tributario",
        "en": "📅 View Tax Calendar",
    },
    "cfo_control_titulo": {
        "es": "✅ Control Interno y Cumplimiento",
        "en": "✅ Internal Control & Compliance",
    },
    "cfo_proceso_auditar": {
        "es": "Proceso a auditar:",
        "en": "Process to audit:",
    },
    "cfo_evaluar_controles": {
        "es": "✅ Evaluar Controles Internos",
        "en": "✅ Evaluate Internal Controls",
    },
    "cfo_mes_regulatorio": {
        "es": "Mes para calendario regulatorio:",
        "en": "Month for regulatory calendar:",
    },
    "cfo_ver_obligaciones": {
        "es": "📋 Ver Obligaciones Regulatorias",
        "en": "📋 View Regulatory Obligations",
    },
    "cfo_reporting_titulo": {
        "es": "📋 Reporting Ejecutivo",
        "en": "📋 Executive Reporting",
    },
    "cfo_reporting_caption": {
        "es": "Genera reportes ejecutivos para Directorio, Matriz o accionistas.",
        "en": "Generate executive reports for Board, Parent Company or shareholders.",
    },
    "cfo_periodo_reporte": {
        "es": "Período del reporte:",
        "en": "Report period:",
    },
    "cfo_kpis_clave": {
        "es": "**KPIs Clave:**",
        "en": "**Key KPIs:**",
    },
    "cfo_logros_periodo": {
        "es": "**Logros del período:**",
        "en": "**Period achievements:**",
    },
    "cfo_generar_reporte": {
        "es": "📋 Generar Reporte Ejecutivo",
        "en": "📋 Generate Executive Report",
    },
    "cfo_reporte_titulo": {
        "es": "### 📋 Reporte Ejecutivo",
        "en": "### 📋 Executive Report",
    },
    "cfo_cargando_matriz": {
        "es": "Cargando matriz de riesgos...",
        "en": "Loading risk matrix...",
    },
    "cfo_cargando_calendario": {
        "es": "Cargando calendario...",
        "en": "Loading calendar...",
    },
    "cfo_cargando_obligaciones": {
        "es": "Cargando obligaciones...",
        "en": "Loading obligations...",
    },
    "cfo_calculando_ratios": {
        "es": "Calculando ratios y generando análisis ejecutivo...",
        "en": "Calculating ratios and generating executive analysis...",
    },
    "cfo_construyendo_presupuesto": {
        "es": "Construyendo presupuesto...",
        "en": "Building budget...",
    },
    "cfo_calculando_caja": {
        "es": "Calculando posición de caja...",
        "en": "Calculating cash position...",
    },
    "cfo_analizando_linea": {
        "es": "Analizando línea bancaria...",
        "en": "Analyzing bank line...",
    },
    "cfo_analizando_wc": {
        "es": "Analizando capital de trabajo...",
        "en": "Analyzing working capital...",
    },
    "cfo_calculando_ir": {
        "es": "Calculando IR...",
        "en": "Calculating income tax...",
    },
    "cfo_calculando_igv": {
        "es": "Calculando IGV...",
        "en": "Calculating VAT...",
    },
    "cfo_evaluando_controles": {
        "es": "Evaluando controles...",
        "en": "Evaluating controls...",
    },
    "cfo_nombre_proyecto": {
        "es": "Nombre del proyecto:",
        "en": "Project name:",
    },
    "cfo_flujos_proyectados": {
        "es": "**Flujos de caja proyectados (S/):**",
        "en": "**Projected cash flows (S/):**",
    },
    "cfo_saldos_banco": {
        "es": "**Saldos por banco (S/):**",
        "en": "**Balances by bank (S/):**",
    },
    "cfo_nombre_riesgo": {
        "es": "Nombre del riesgo:",
        "en": "Risk name:",
    },
    "cfo_categoria": {
        "es": "Categoría:",
        "en": "Category:",
    },
    "cfo_probabilidad": {
        "es": "Probabilidad:",
        "en": "Probability:",
    },
    "cfo_impacto": {
        "es": "Impacto (% de ingresos):",
        "en": "Impact (% of revenue):",
    },
    "cfo_ingresos_anuales": {
        "es": "Ingresos anuales (S/):",
        "en": "Annual revenue (S/):",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL DE TRADUCCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def t(key: str, lang: str = "es") -> str:
    """
    Retorna el texto en el idioma seleccionado.
    Si la clave no existe, retorna la clave misma como fallback.
    """
    entry = TEXTS.get(key)
    if entry is None:
        return key  # fallback: retorna la clave
    return entry.get(lang, entry.get("es", key))


# ─────────────────────────────────────────────────────────────────────────────
# SECTORES TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

SECTORS = {
    "es": {
        "mining":     "⛏️ Minería y Energía",
        "banking":    "🏦 Banca y Seguros",
        "retail":     "🛒 Retail y Comercio",
        "health":     "🏥 Salud y Farmacia",
        "government": "🏛️ Gobierno y Sector Público",
    },
    "en": {
        "mining":     "⛏️ Mining & Energy",
        "banking":    "🏦 Banking & Insurance",
        "retail":     "🛒 Retail & Commerce",
        "health":     "🏥 Health & Pharma",
        "government": "🏛️ Government & Public Sector",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# MÓDULOS CFO TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

MODULES = {
    "es": [
        "🤖 Chat Ejecutivo",
        "📊 Análisis Financiero",
        "📈 Planeamiento",
        "🏦 Tesorería y Bancos",
        "⚠️ Gestión de Riesgos",
        "🧾 Impuestos",
        "✅ Control Interno",
        "📋 Reporting",
    ],
    "en": [
        "🤖 Executive Chat",
        "📊 Financial Analysis",
        "📈 Planning",
        "🏦 Treasury & Banks",
        "⚠️ Risk Management",
        "🧾 Taxes",
        "✅ Internal Control",
        "📋 Reporting",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# TEMAS DEL PROGRAMA EDUCATIVO TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

PROGRAM_TOPICS = {
    "es": {
        "🔢 Análisis Financiero": [
            "Ratios de liquidez", "Ratios de rentabilidad",
            "Análisis de estados financieros", "Benchmarking sectorial"
        ],
        "📊 Planeamiento": [
            "Presupuesto maestro", "Forecasting y escenarios",
            "Evaluación CAPEX (VPN, TIR)", "Análisis de variaciones"
        ],
        "⚠️ Gestión de Riesgos": [
            "Matriz de riesgos", "Value at Risk (VaR)",
            "Riesgo de mercado y crédito", "Planes de mitigación"
        ],
        "🏦 Tesorería y Bancos": [
            "Posición de caja diaria", "Proyección de flujo de caja",
            "Gestión de líneas bancarias", "Capital de trabajo (CCC)"
        ],
        "🧾 Impuestos": [
            "Impuesto a la Renta Perú", "IGV y posición fiscal",
            "Calendario SUNAT", "Optimización tributaria"
        ],
        "✅ Control Interno": [
            "Segregación de funciones", "Controles por proceso",
            "Auditoría interna", "Cumplimiento regulatorio"
        ],
    },
    "en": {
        "🔢 Financial Analysis": [
            "Liquidity ratios", "Profitability ratios",
            "Financial statement analysis", "Sector benchmarking"
        ],
        "📊 Planning": [
            "Master budget", "Forecasting & scenarios",
            "CAPEX evaluation (NPV, IRR)", "Variance analysis"
        ],
        "⚠️ Risk Management": [
            "Risk matrix", "Value at Risk (VaR)",
            "Market & credit risk", "Mitigation plans"
        ],
        "🏦 Treasury & Banks": [
            "Daily cash position", "Cash flow projection",
            "Bank line management", "Working capital (CCC)"
        ],
        "🧾 Taxes": [
            "Peru Income Tax", "VAT & tax position",
            "SUNAT calendar", "Tax optimization"
        ],
        "✅ Internal Control": [
            "Segregation of duties", "Process controls",
            "Internal audit", "Regulatory compliance"
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# PROCESOS DE AUDITORÍA TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

AUDIT_PROCESSES = {
    "es": {
        "cuentas_por_pagar":  "💳 Cuentas por Pagar",
        "cuentas_por_cobrar": "📥 Cuentas por Cobrar",
        "nomina":             "👥 Nómina y Planilla",
        "tesoreria":          "💰 Tesorería",
        "inventarios":        "📦 Inventarios",
    },
    "en": {
        "cuentas_por_pagar":  "💳 Accounts Payable",
        "cuentas_por_cobrar": "📥 Accounts Receivable",
        "nomina":             "👥 Payroll",
        "tesoreria":          "💰 Treasury",
        "inventarios":        "📦 Inventory",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORÍAS DE RIESGO TRADUCIDAS
# ─────────────────────────────────────────────────────────────────────────────

RISK_CATEGORIES = {
    "es": ["Mercado", "Operacional", "Financiero", "Regulatorio", "Tecnológico", "Integridad"],
    "en": ["Market", "Operational", "Financial", "Regulatory", "Technological", "Integrity"],
}


# ─────────────────────────────────────────────────────────────────────────────
# REGÍMENES TRIBUTARIOS TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

TAX_REGIMES = {
    "es": {
        "general":  "General (29.5%)",
        "mype":     "MYPE (10%)",
        "especial": "Especial (1.5%)",
    },
    "en": {
        "general":  "General Regime (29.5%)",
        "mype":     "SME Regime (10%)",
        "especial": "Special Regime (1.5%)",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# NIVELES DE ALUMNO TRADUCIDOS
# ─────────────────────────────────────────────────────────────────────────────

STUDENT_LEVELS = {
    "es": {
        "basico":      "🟡 Básico",
        "intermedio":  "🔵 Intermedio",
        "avanzado":    "🟢 Avanzado",
    },
    "en": {
        "basico":      "🟡 Basic",
        "intermedio":  "🔵 Intermediate",
        "avanzado":    "🟢 Advanced",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# COLUMNAS DEL RANKING TRADUCIDAS
# ─────────────────────────────────────────────────────────────────────────────

RANKING_COLUMNS = {
    "es": {
        "alumno":             "Alumno",
        "promedio":           "Promedio",
        "semaforo":           "Estado",
        "nivel":              "Nivel",
        "total_evaluaciones": "Evaluaciones",
        "ultima_actividad":   "Última Actividad",
    },
    "en": {
        "alumno":             "Student",
        "promedio":           "Average",
        "semaforo":           "Status",
        "nivel":              "Level",
        "total_evaluaciones": "Evaluations",
        "ultima_actividad":   "Last Activity",
    },
}