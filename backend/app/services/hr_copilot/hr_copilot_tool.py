# backend/app/services/hr_copilot/hr_copilot_tool.py

from typing import List, Dict

class HRCopilotTool:
    """
    Asier: aquí luego podrás llamar a un LLM o usar reglas.
    De momento devolvemos un JSON dummy, con estructura correcta.
    """

    def run(self, answers: List[str]) -> Dict:
        joined = " ".join(answers)

        # TODO: análisis real. Esto es dummy.
        return {
            "motivaciones": "Aprender, aportar impacto y trabajar en equipo.",
            "experiencia_clave": ["Proyecto universitario", "Prácticas en empresa demo"],
            "valores_detectados": ["innovacion", "colaboracion"],
            "soft_skills": ["comunicacion", "adaptabilidad"],
            "preferencias_equipo": "Equipos pequenos con buen ambiente.",
            "resumen_psicologico": "Perfil proactivo, con ganas de aprender y contribuir."
        }
