# backend/app/services/hr_copilot/questions.py

"""
Preguntas estándar de la llamada IA de RRHH.
Estas preguntas se usan para la entrevista inicial con el candidato.
"""

INTERVIEW_QUESTIONS = [
    {
        "id": 1,
        "question": "¿Qué te motiva de este puesto y por qué te interesa trabajar con nosotros?",
        "category": "motivacion",
        "description": "Evalúa la motivación intrínseca y el alineamiento con la empresa"
    },
    {
        "id": 2,
        "question": "Cuéntame sobre un proyecto del que estés especialmente orgulloso. ¿Qué hiciste y qué aprendiste?",
        "category": "experiencia",
        "description": "Identifica experiencias clave y capacidad de aprendizaje"
    },
    {
        "id": 3,
        "question": "¿En qué tipo de equipo te sientes más cómodo y rindes mejor?",
        "category": "team_fit",
        "description": "Detecta preferencias de trabajo en equipo y cultura"
    },
    {
        "id": 4,
        "question": "¿Qué valor personal o principio te define más en tu forma de trabajar?",
        "category": "valores",
        "description": "Extrae valores fundamentales del candidato"
    },
    {
        "id": 5,
        "question": "¿Cómo manejas situaciones de alta presión o cuando las cosas no salen según lo planeado?",
        "category": "soft_skills",
        "description": "Identifica soft skills como resiliencia y adaptabilidad"
    }
]

def get_questions() -> list:
    """Retorna la lista de preguntas de la entrevista"""
    return INTERVIEW_QUESTIONS

def get_questions_text() -> list:
    """Retorna solo el texto de las preguntas"""
    return [q["question"] for q in INTERVIEW_QUESTIONS]

def get_question_by_id(question_id: int) -> dict:
    """Obtiene una pregunta específica por ID"""
    for q in INTERVIEW_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None

