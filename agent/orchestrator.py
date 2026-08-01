"""
CFO Agent IA - Orchestrator Central con Soporte Bilingüe
Coordina todos los sub-agentes y herramientas mediante Gemini Function Calling
"""
import google.generativeai as genai
import json
from datetime import datetime

from tools.financial_tools import calculate_financial_ratios, analyze_financial_statement
from tools.planning_tools import build_budget, run_forecast, evaluate_capex, compare_budget_vs_actual
from tools.treasury_tools import (
    get_daily_cash_position, project_cash_flow,
    manage_bank_lines, optimize_working_capital,
    get_tax_calendar, calculate_income_tax, compute_igv_position
)
from tools.risk_compliance_tools import (
    assess_risk, get_risk_matrix, calculate_var,
    audit_internal_controls, check_regulatory_calendar,
    generate_executive_summary
)
from tools.student_tools import (
    get_student_profile, save_evaluation,
    generate_quiz, send_alert_to_professor
)
from memory.database import StudentMemory
from prompts.system_prompts import get_system_prompt


# ─────────────────────────────────────────────────────────────────────────────
# DEFINICIÓN DE HERRAMIENTAS PARA FUNCTION CALLING
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DECLARATIONS = [
    genai.protos.Tool(function_declarations=[

        # ── FINANCIERAS ──────────────────────────────────────────────────────
        genai.protos.FunctionDeclaration(
            name="calculate_financial_ratios",
            description="Calculates complete financial ratios: liquidity, solvency, profitability and efficiency. Use when the user asks about ratios, KPIs or financial indicators.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "activo_corriente":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "pasivo_corriente":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "activo_total":        genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "pasivo_total":        genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "patrimonio":          genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "utilidad_neta":       genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "utilidad_operativa":  genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "ventas":              genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "inventario":          genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "ebitda":              genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "deuda_financiera":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["activo_corriente", "pasivo_corriente"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="analyze_financial_statement",
            description="Analyzes Balance Sheet, Income Statement or Cash Flow with sector benchmarks.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "statement_type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        enum=["balance_general", "estado_resultados", "flujo_caja"]
                    ),
                    "data":   genai.protos.Schema(type=genai.protos.Type.STRING),
                    "sector": genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["statement_type", "data"]
            )
        ),

        # ── PLANEAMIENTO ─────────────────────────────────────────────────────
        genai.protos.FunctionDeclaration(
            name="build_budget",
            description="Builds annual budget with monthly distribution, by department and key assumptions.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "year":          genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    "revenue_base":  genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "growth_rate":   genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "cost_ratio":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "opex_ratio":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "sector":        genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["year", "revenue_base"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="run_forecast",
            description="Projects annual revenue under base, optimistic and pessimistic scenarios.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "revenue_ytd":            genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "months_elapsed":         genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    "scenario":               genai.protos.Schema(type=genai.protos.Type.STRING, enum=["base", "optimista", "pesimista"]),
                    "commodity_price_change": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["revenue_ytd", "months_elapsed"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="evaluate_capex",
            description="Evaluates CAPEX investment project: NPV, IRR, Payback and Profitability Index.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "project_name":      genai.protos.Schema(type=genai.protos.Type.STRING),
                    "inversion_inicial": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "flujos_caja":       genai.protos.Schema(type=genai.protos.Type.STRING),
                    "tasa_descuento":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "vida_util":         genai.protos.Schema(type=genai.protos.Type.INTEGER),
                },
                required=["project_name", "inversion_inicial", "flujos_caja"]
            )
        ),

        # ── TESORERÍA ────────────────────────────────────────────────────────
        genai.protos.FunctionDeclaration(
            name="get_daily_cash_position",
            description="Calculates consolidated daily cash position with liquidity alerts.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "saldo_bancos":                genai.protos.Schema(type=genai.protos.Type.STRING),
                    "cobros_pendientes":           genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "pagos_pendientes":            genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "lineas_credito_disponibles":  genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["saldo_bancos"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="manage_bank_lines",
            description="Manages bank credit lines: availability, financial cost and maturity alerts.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "banco":           genai.protos.Schema(type=genai.protos.Type.STRING),
                    "tipo_linea":      genai.protos.Schema(type=genai.protos.Type.STRING),
                    "monto_linea":     genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "monto_utilizado": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "tasa_interes":    genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "vencimiento":     genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["banco", "tipo_linea", "monto_linea", "monto_utilizado", "tasa_interes", "vencimiento"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="get_tax_calendar",
            description="Returns SUNAT tax calendar for the indicated month (Peru).",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "mes": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    "año": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                },
                required=["mes"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="calculate_income_tax",
            description="Calculates Income Tax according to Peruvian tax regime (general, mype, especial).",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "utilidad_antes_impuestos":  genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "adiciones":                 genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "deducciones":               genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "pagos_cuenta_realizados":   genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "regimen":                   genai.protos.Schema(type=genai.protos.Type.STRING, enum=["general", "mype", "especial"]),
                },
                required=["utilidad_antes_impuestos"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="compute_igv_position",
            description="Calculates monthly VAT position: tax debit vs tax credit.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "igv_ventas":           genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "igv_compras":          genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "saldo_favor_anterior": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["igv_ventas", "igv_compras"]
            )
        ),

        # ── RIESGOS Y CUMPLIMIENTO ───────────────────────────────────────────
        genai.protos.FunctionDeclaration(
            name="assess_risk",
            description="Evaluates a specific risk with scoring, expected loss and required action.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "nombre_riesgo":      genai.protos.Schema(type=genai.protos.Type.STRING),
                    "categoria":          genai.protos.Schema(type=genai.protos.Type.STRING),
                    "probabilidad":       genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "impacto":            genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "ingresos_anuales":   genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["nombre_riesgo", "categoria", "probabilidad", "impacto"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="get_risk_matrix",
            description="Gets the complete sector risk matrix with scoring and prioritization.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "sector": genai.protos.Schema(type=genai.protos.Type.STRING, enum=["mining", "banking", "retail", "health", "government"]),
                },
                required=["sector"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="audit_internal_controls",
            description="Evaluates internal controls of an accounting/financial process and generates gap checklist.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "proceso": genai.protos.Schema(type=genai.protos.Type.STRING,
                                                   enum=["cuentas_por_pagar", "cuentas_por_cobrar", "nomina", "tesoreria", "inventarios"]),
                    "sector":  genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["proceso"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="check_regulatory_calendar",
            description="Returns regulatory obligations for the month for the indicated sector and country.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "mes":    genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    "año":    genai.protos.Schema(type=genai.protos.Type.INTEGER),
                    "pais":   genai.protos.Schema(type=genai.protos.Type.STRING),
                    "sector": genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["mes"]
            )
        ),

        # ── EDUCATIVAS ───────────────────────────────────────────────────────
        genai.protos.FunctionDeclaration(
            name="get_student_profile",
            description="Gets the complete student profile: level, progress, weak topics and recommendations.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "student_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["student_id"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="generate_quiz",
            description="Generates evaluation questions adapted to the student's level and topic.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "topic":         genai.protos.Schema(type=genai.protos.Type.STRING),
                    "difficulty":    genai.protos.Schema(type=genai.protos.Type.STRING, enum=["basico", "intermedio", "avanzado"]),
                    "student_id":    genai.protos.Schema(type=genai.protos.Type.STRING),
                    "num_questions": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                },
                required=["topic"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="save_evaluation",
            description="Saves the student's grade and updates their learning profile.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "student_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                    "topic":      genai.protos.Schema(type=genai.protos.Type.STRING),
                    "score":      genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "max_score":  genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["student_id", "topic", "score"]
            )
        ),

        genai.protos.FunctionDeclaration(
            name="send_alert_to_professor",
            description="Sends alert to teacher about students with low performance, achievements or inactivity.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "mensaje":      genai.protos.Schema(type=genai.protos.Type.STRING),
                    "student_ids":  genai.protos.Schema(type=genai.protos.Type.STRING),
                    "tipo_alerta":  genai.protos.Schema(type=genai.protos.Type.STRING,
                                                        enum=["bajo_rendimiento", "logro_destacado", "inactividad", "dificultad_tema"]),
                    "urgencia":     genai.protos.Schema(type=genai.protos.Type.STRING, enum=["alta", "media", "baja"]),
                },
                required=["mensaje", "student_ids", "tipo_alerta"]
            )
        ),
    ])
]


# ─────────────────────────────────────────────────────────────────────────────
# MAPA DE EJECUCIÓN DE HERRAMIENTAS
# ─────────────────────────────────────────────────────────────────────────────

def _execute_tool(function_call) -> dict:
    """Ejecuta la herramienta solicitada por el modelo y retorna el resultado."""
    name = function_call.name
    args = dict(function_call.args)

    for key in ["data", "flujos_caja", "saldo_bancos", "student_ids"]:
        if key in args and isinstance(args[key], str):
            try:
                args[key] = json.loads(args[key])
            except Exception:
                pass

    tool_map = {
        "calculate_financial_ratios":  lambda a: calculate_financial_ratios(**a),
        "analyze_financial_statement": lambda a: analyze_financial_statement(**a),
        "build_budget":                lambda a: build_budget(**a),
        "run_forecast":                lambda a: run_forecast(**a),
        "evaluate_capex":              lambda a: evaluate_capex(**a),
        "compare_budget_vs_actual":    lambda a: compare_budget_vs_actual(**a),
        "get_daily_cash_position":     lambda a: get_daily_cash_position(**a),
        "manage_bank_lines":           lambda a: manage_bank_lines(**a),
        "optimize_working_capital":    lambda a: optimize_working_capital(**a),
        "get_tax_calendar":            lambda a: get_tax_calendar(**a),
        "calculate_income_tax":        lambda a: calculate_income_tax(**a),
        "compute_igv_position":        lambda a: compute_igv_position(**a),
        "assess_risk":                 lambda a: assess_risk(**a),
        "get_risk_matrix":             lambda a: get_risk_matrix(**a),
        "calculate_var":               lambda a: calculate_var(**a),
        "audit_internal_controls":     lambda a: audit_internal_controls(**a),
        "check_regulatory_calendar":   lambda a: check_regulatory_calendar(**a),
        "generate_executive_summary":  lambda a: generate_executive_summary(**a),
        "get_student_profile":         lambda a: get_student_profile(**a),
        "save_evaluation":             lambda a: save_evaluation(**a),
        "generate_quiz":               lambda a: generate_quiz(**a),
        "send_alert_to_professor":     lambda a: send_alert_to_professor(**a),
    }

    handler = tool_map.get(name)
    if handler:
        try:
            result = handler(args)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e), "tool": name}
    return {"status": "error", "error": f"Tool '{name}' not found"}


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR PRINCIPAL (con soporte bilingüe)
# ─────────────────────────────────────────────────────────────────────────────

class CFOOrchestrator:
    """
    Agente coordinador central del CFO Agent IA.
    Soporta tres modos: tutor, cfo, professor.
    Soporta dos idiomas: es (español), en (English).
    """

    def __init__(
        self,
        api_key: str,
        mode: str = "tutor",
        sector: str = "mining",
        model_name: str = "models/gemini-3.6-flash",
        lang: str = "es",                        # ← NUEVO: parámetro de idioma
    ):
        genai.configure(api_key=api_key)
        self.mode = mode
        self.sector = sector
        self.lang = lang                          # ← NUEVO: guardar idioma
        self.memory = StudentMemory()
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=get_system_prompt(mode, sector, lang),  # ← pasa lang
            tools=TOOL_DECLARATIONS,
        )
        self.chat_sessions = {}

    def update_language(self, lang: str, api_key: str, model_name: str = "models/gemini-3.6-flash"):
        """
        Actualiza el idioma del agente recreando el modelo con el nuevo system prompt.
        Llama a este método cuando el usuario cambia el idioma en la UI.
        """
        if lang != self.lang:
            self.lang = lang
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=get_system_prompt(self.mode, self.sector, lang),
                tools=TOOL_DECLARATIONS,
            )
            # Limpiar sesiones para que el agente reinicie con el nuevo idioma
            self.chat_sessions = {}

    def get_or_create_chat(self, session_id: str, history: list = None):
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = self.model.start_chat(
                history=history or []
            )
        return self.chat_sessions[session_id]

    def run(
        self,
        user_message: str,
        session_id: str = "default",
        student_id: str = None,
        history: list = None,
        max_tool_calls: int = 5,
    ) -> dict:
        """Ejecuta el ciclo ReAct completo: Observe → Think → Act → Observe Result → Respond"""
        chat = self.get_or_create_chat(session_id, history)
        tools_used = []
        start_time = datetime.now()

        try:
            response = chat.send_message(user_message)

            tool_calls = 0
            while tool_calls < max_tool_calls:
                parts = response.candidates[0].content.parts
                has_function_call = any(hasattr(p, "function_call") and p.function_call.name for p in parts)

                if not has_function_call:
                    break

                function_responses = []
                for part in parts:
                    if hasattr(part, "function_call") and part.function_call.name:
                        tool_result = _execute_tool(part.function_call)
                        tools_used.append(part.function_call.name)
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=part.function_call.name,
                                    response={"result": str(tool_result)}
                                )
                            )
                        )

                response = chat.send_message(
                    genai.protos.Content(parts=function_responses)
                )
                tool_calls += 1

            final_text = response.text
            elapsed = (datetime.now() - start_time).total_seconds()

            if student_id:
                self.memory.save_interaction(
                    student_id=student_id,
                    message=user_message,
                    response=final_text,
                    topic=self._detect_topic(user_message),
                )
            else:
                self.memory.save_cfo_session(
                    user_id=session_id,
                    module=self.mode,
                    query=user_message,
                    response=final_text,
                    tools_used=tools_used,
                )

            return {
                "response": final_text,
                "tools_used": tools_used,
                "tool_calls_count": tool_calls,
                "elapsed_seconds": round(elapsed, 2),
                "mode": self.mode,
                "sector": self.sector,
                "lang": self.lang,
            }

        except Exception as e:
            return {
                "response": f"Error en el agente / Agent error: {str(e)}",
                "tools_used": tools_used,
                "error": str(e),
            }

    def _detect_topic(self, message: str) -> str:
        topics = {
            "ratios":       ["ratio", "liquidez", "roe", "roa", "margen", "solvencia", "liquidity", "profitability"],
            "presupuesto":  ["presupuesto", "budget", "forecast", "proyección", "projection"],
            "flujo_caja":   ["flujo", "caja", "cash", "tesorería", "treasury"],
            "riesgos":      ["riesgo", "risk", "var", "volatilidad", "volatility"],
            "impuestos":    ["igv", "impuesto", "sunat", "renta", "tributario", "tax", "vat"],
            "capex":        ["capex", "inversión", "investment", "proyecto", "project", "vpn", "npv", "tir", "irr"],
            "bancos":       ["banco", "bank", "línea", "line", "crédito", "credit"],
        }
        msg_lower = message.lower()
        for topic, keywords in topics.items():
            if any(kw in msg_lower for kw in keywords):
                return topic
        return "general"

    def reset_session(self, session_id: str):
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
