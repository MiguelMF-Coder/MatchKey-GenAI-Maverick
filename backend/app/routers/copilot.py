from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import json

from ..services.hr_copilot.hr_copilot_tool import get_hr_copilot
from ..services.hr_copilot.questions import get_questions, get_questions_text

router = APIRouter(prefix="/copilot", tags=["copilot"])

# Lazy load del HR Copilot
_hr_instance = None

def get_hr():
    global _hr_instance
    if _hr_instance is None:
        _hr_instance = get_hr_copilot()
    return _hr_instance


class ProcessCallRequest(BaseModel):
    """Request para procesar llamada de RRHH"""
    candidate_id: int
    answers: List[str]
    questions: Optional[List[str]] = None


class ProcessCallResponse(BaseModel):
    """Response con análisis completo"""
    candidate_id: int
    motivaciones: str
    experiencia_clave: List[str]
    valores_detectados: List[str]
    soft_skills: List[str]
    preferencias_equipo: str
    resumen_psicologico: str
    success: bool = True


@router.get("/questions")
def get_interview_questions():
    """
    Obtiene las preguntas estándar de la entrevista de RRHH.

    Returns:
        Lista de preguntas con metadata
    """
    return {
        "questions": get_questions(),
        "total": len(get_questions())
    }


@router.post("/process_call", response_model=ProcessCallResponse)
def process_call(request: ProcessCallRequest):
    """
    Procesa las respuestas de una llamada de RRHH y extrae insights.

    Args:
        request: Datos de la llamada con candidate_id y respuestas

    Returns:
        Análisis estructurado del candidato
    """
    try:
        hr = get_hr()

        # Validar que hay respuestas
        if not request.answers or not any(request.answers):
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos algunas respuestas del candidato"
            )

        # Analizar respuestas
        result = hr.run(
            answers=request.answers,
            questions=request.questions
        )

        # Agregar candidate_id al resultado
        result["candidate_id"] = request.candidate_id
        result["success"] = True

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la llamada: {str(e)}"
        )


@router.post("/process_call_audio")
async def process_call_audio(
    candidate_id: int,
    audio_files: List[UploadFile] = File(...),
    language: str = "es"
):
    """
    Procesa respuestas de audio de una llamada de RRHH.

    Args:
        candidate_id: ID del candidato
        audio_files: Archivos de audio (uno por pregunta)
        language: Código de idioma (es, en, etc.)

    Returns:
        Análisis estructurado + transcripciones
    """
    try:
        hr = get_hr()

        # Guardar archivos temporalmente y procesar
        import tempfile
        import os

        temp_files = []
        try:
            # Guardar uploads temporalmente
            for upload in audio_files:
                suffix = os.path.splitext(upload.filename)[1] or ".wav"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    content = await upload.read()
                    tmp.write(content)
                    temp_files.append(tmp.name)

            # Analizar audios
            result = hr.analyze_audio(
                audio_files=temp_files,
                language=language
            )

            result["candidate_id"] = candidate_id
            result["success"] = True

            return result

        finally:
            # Limpiar archivos temporales
            for tmp_file in temp_files:
                try:
                    os.unlink(tmp_file)
                except:
                    pass

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando audio: {str(e)}"
        )


@router.get("/health")
def health_check():
    """
    Verifica el estado del HR Copilot.

    Returns:
        Estado del servicio y configuración
    """
    import os

    hr = get_hr()

    return {
        "status": "healthy",
        "groq_configured": hr.api_key is not None,
        "model": hr.model,
        "whisper_model": hr.audio_processor.model,
        "whisper_api": "groq",  # Indica que usa Groq API en lugar de local
        "questions_count": len(get_questions())
    }

