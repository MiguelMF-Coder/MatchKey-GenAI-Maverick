# backend/app/services/hr_copilot/prompt_templates.py

"""
Plantillas de prompts para el análisis semántico de entrevistas.
Usados con Groq API para extraer insights de candidatos.
"""

SYSTEM_PROMPT = """Eres un analista experto de RRHH especializado en evaluación de talento.
Tu tarea es analizar respuestas de candidatos en entrevistas y extraer información estructurada.

Debes identificar:
1. MOTIVACIONES: Qué impulsa al candidato, qué le apasiona, qué busca en su carrera
2. EXPERIENCIA CLAVE: Proyectos, logros o situaciones destacables que menciona
3. VALORES DETECTADOS: Principios y valores que demuestra (innovación, colaboración, ética, autonomía, impacto social, excelencia, etc.)
4. SOFT SKILLS: Habilidades blandas evidentes (comunicación, liderazgo, adaptabilidad, resiliencia, trabajo en equipo, pensamiento crítico, etc.)
5. PREFERENCIAS DE EQUIPO: Tipo de ambiente laboral donde mejor rinde
6. RESUMEN PSICOLÓGICO: Perfil general del candidato en 2-3 oraciones

Sé preciso, objetivo y basa tus conclusiones únicamente en lo que el candidato dice explícitamente o implica claramente."""

BASE_PROMPT = """Analiza las siguientes respuestas de un candidato a una entrevista de RRHH.

PREGUNTAS Y RESPUESTAS:
{qa_pairs}

Extrae la información siguiendo estas instrucciones:

1. **Motivaciones**: Resume en 2-3 oraciones qué motiva al candidato profesionalmente
2. **Experiencia clave**: Lista 2-4 experiencias, proyectos o logros mencionados
3. **Valores detectados**: Identifica 3-5 valores fundamentales (usa: innovación, colaboración, ética, autonomía, impacto_social, excelencia, transparencia, diversidad, sostenibilidad, aprendizaje_continuo)
4. **Soft skills**: Identifica 3-6 habilidades blandas (usa: comunicación, liderazgo, adaptabilidad, resiliencia, trabajo_equipo, pensamiento_crítico, empatía, creatividad, organización, proactividad)
5. **Preferencias de equipo**: Describe en 1-2 oraciones el ambiente laboral preferido
6. **Resumen psicológico**: Perfil general en 2-3 oraciones

Responde ÚNICAMENTE con un JSON válido en el siguiente formato (sin markdown, sin explicaciones adicionales):

{{
  "motivaciones": "texto aquí",
  "experiencia_clave": ["experiencia 1", "experiencia 2"],
  "valores_detectados": ["valor1", "valor2", "valor3"],
  "soft_skills": ["skill1", "skill2", "skill3"],
  "preferencias_equipo": "texto aquí",
  "resumen_psicologico": "texto aquí"
}}"""

FALLBACK_VALUES = {
    "motivaciones": "El candidato busca desarrollo profesional y aportar valor en un entorno colaborativo.",
    "experiencia_clave": ["Experiencia en proyectos técnicos", "Capacidad de aprendizaje demostrada"],
    "valores_detectados": ["profesionalismo", "aprendizaje_continuo", "colaboración"],
    "soft_skills": ["comunicación", "adaptabilidad", "trabajo_equipo"],
    "preferencias_equipo": "Prefiere equipos colaborativos con buena comunicación.",
    "resumen_psicologico": "Candidato con actitud positiva y disposición para el aprendizaje continuo."
}

def format_qa_pairs(questions: list, answers: list) -> str:
    """
    Formatea las preguntas y respuestas para el prompt.

    Args:
        questions: Lista de textos de preguntas
        answers: Lista de respuestas del candidato

    Returns:
        String formateado con Q&A
    """
    qa_text = []
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_text.append(f"PREGUNTA {i}: {q}")
        qa_text.append(f"RESPUESTA {i}: {a}")
        qa_text.append("")

    return "\n".join(qa_text)

def build_analysis_prompt(questions: list, answers: list) -> str:
    """
    Construye el prompt completo para análisis.

    Args:
        questions: Lista de preguntas
        answers: Lista de respuestas

    Returns:
        Prompt formateado listo para enviar al LLM
    """
    qa_pairs = format_qa_pairs(questions, answers)
    return BASE_PROMPT.format(qa_pairs=qa_pairs)
