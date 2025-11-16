# backend/app/services/hr_copilot/prompt_templates.py

BASE_PROMPT = """
Eres un analista de RRHH.
Dado el siguiente conjunto de respuestas de un candidato, devuelve un JSON con:

- motivaciones
- experiencia_clave (lista)
- valores_detectados (lista)
- soft_skills (lista)
- preferencias_equipo
- resumen_psicologico
"""
