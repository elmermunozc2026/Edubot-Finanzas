office_agent@computer:~$
find cfo_agent_ia -name "*.py" | sort && echo "---TOTAL---" && find cfo_agent_ia -name "*.py" | wc -l && echo "---LÍNEAS---" && find cfo_agent_ia -name "*.py" -exec wc -l {} + | tail -1
cfo_agent_ia/agent/orchestrator.py
cfo_agent_ia/app.py
cfo_agent_ia/check_model.py
cfo_agent_ia/i18n/translations.py
cfo_agent_ia/memory/database.py
cfo_agent_ia/pages/1_Alumno.py
cfo_agent_ia/pages/2_Profesor.py
cfo_agent_ia/pages/3_CFO_Asistente.py
cfo_agent_ia/prompts/system_prompts.py
cfo_agent_ia/tools/financial_tools.py
cfo_agent_ia/tools/planning_tools.py
cfo_agent_ia/tools/risk_compliance_tools.py
cfo_agent_ia/tools/student_tools.py
cfo_agent_ia/tools/treasury_tools.py
---TOTAL---
14
---LÍNEAS---
  4770 total
office_agent@computer:~$ _
