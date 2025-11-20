# backend/app/services/hr_copilot/hr_copilot_tool.py

"""
HR Copilot Tool - Agente de IA para análisis de entrevistas de RRHH.
Procesa respuestas de candidatos y extrae motivaciones, valores, soft skills y preferencias.
Implementado como herramienta MCP usando Groq API.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv

from .prompt_templates import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    FALLBACK_VALUES
)
from .questions import get_questions_text
from .audio_processor import AudioProcessor

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


class HRCopilotTool:
    """
    Herramienta MCP para análisis de entrevistas de RRHH.

    Funcionalidades:
    - Analiza respuestas de texto de candidatos
    - Transcribe y analiza respuestas de audio
    - Extrae insights estructurados (motivaciones, valores, soft skills)
    - Devuelve JSON estandarizado para integración con sistema
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        whisper_model: str = "base",
        temperature: float = 0.3
    ):
        """
        Inicializa el HR Copilot Tool.

        Args:
            api_key: Groq API key (si no se provee, se lee de GROQ_API_KEY env var)
            model: Modelo de Groq a usar (llama-3.3-70b-versatile, mixtral-8x7b-32768, etc.)
            whisper_model: Tamaño del modelo Whisper (tiny, base, small, medium, large)
            temperature: Temperatura para generación (0.0-1.0, menor = más determinístico)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY no configurada. El análisis semántico no funcionará.")

        self.model = model
        self.temperature = temperature
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.audio_processor = AudioProcessor(model_size=whisper_model)

        logger.info(f"HRCopilotTool inicializado - Modelo: {model}, Whisper: {whisper_model}")

    def _call_groq_api(self, user_prompt: str) -> Optional[str]:
        """
        Llama a Groq API para análisis semántico.

        Args:
            user_prompt: Prompt con las respuestas del candidato

        Returns:
            Respuesta del modelo o None si falla
        """
        if not self.client:
            logger.error("Cliente Groq no inicializado. Verifica GROQ_API_KEY")
            return None

        try:
            logger.info(f"Llamando a Groq API con modelo {self.model}...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=2000,
                top_p=1,
                stream=False
            )

            result = response.choices[0].message.content
            logger.info(f"Respuesta recibida de Groq ({len(result)} caracteres)")

            return result

        except Exception as e:
            logger.error(f"Error llamando a Groq API: {str(e)}")
            return None

    def _parse_json_response(self, response: str) -> Optional[dict]:
        """
        Parsea la respuesta JSON del modelo.

        Args:
            response: String de respuesta del modelo

        Returns:
            Dict parseado o None si falla
        """
        try:
            # Limpiar markdown si existe
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parsear JSON
            data = json.loads(response)

            # Validar estructura básica
            required_keys = [
                "motivaciones",
                "experiencia_clave",
                "valores_detectados",
                "soft_skills",
                "preferencias_equipo",
                "resumen_psicologico"
            ]

            for key in required_keys:
                if key not in data:
                    logger.warning(f"Clave faltante en respuesta: {key}")
                    return None

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            logger.debug(f"Respuesta recibida: {response[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado parseando respuesta: {str(e)}")
            return None

    def _validate_and_clean_result(self, data: dict) -> dict:
        """
        Valida y limpia el resultado del análisis.

        Args:
            data: Dict con datos del análisis

        Returns:
            Dict validado y limpio
        """
        # Asegurar que listas sean listas
        if isinstance(data.get("experiencia_clave"), str):
            data["experiencia_clave"] = [data["experiencia_clave"]]
        if isinstance(data.get("valores_detectados"), str):
            data["valores_detectados"] = [data["valores_detectados"]]
        if isinstance(data.get("soft_skills"), str):
            data["soft_skills"] = [data["soft_skills"]]

        # Normalizar valores (lowercase, guiones bajos)
        data["valores_detectados"] = [
            v.lower().replace(" ", "_").replace("-", "_")
            for v in data.get("valores_detectados", [])
        ]
        data["soft_skills"] = [
            s.lower().replace(" ", "_").replace("-", "_")
            for s in data.get("soft_skills", [])
        ]

        # Limitar longitudes
        data["motivaciones"] = data.get("motivaciones", "")[:1000]
        data["preferencias_equipo"] = data.get("preferencias_equipo", "")[:500]
        data["resumen_psicologico"] = data.get("resumen_psicologico", "")[:1000]

        data["experiencia_clave"] = data.get("experiencia_clave", [])[:6]
        data["valores_detectados"] = data.get("valores_detectados", [])[:8]
        data["soft_skills"] = data.get("soft_skills", [])[:10]

        return data

    def analyze_answers(
        self,
        answers: List[str],
        questions: Optional[List[str]] = None
    ) -> Dict:
        """
        Analiza respuestas de texto del candidato.

        Args:
            answers: Lista de respuestas del candidato
            questions: Lista de preguntas (opcional, usa las estándar si no se provee)

        Returns:
            Dict con análisis estructurado:
                - motivaciones: str
                - experiencia_clave: List[str]
                - valores_detectados: List[str]
                - soft_skills: List[str]
                - preferencias_equipo: str
                - resumen_psicologico: str
        """
        # Validar entrada
        if not answers or not any(answers):
            logger.warning("No se proporcionaron respuestas válidas")
            return FALLBACK_VALUES.copy()

        # Usar preguntas estándar si no se proveen
        if questions is None:
            questions = get_questions_text()

        # Asegurar mismo número de preguntas y respuestas
        if len(questions) != len(answers):
            logger.warning(f"Número de preguntas ({len(questions)}) != respuestas ({len(answers)})")
            # Ajustar si es necesario
            min_len = min(len(questions), len(answers))
            questions = questions[:min_len]
            answers = answers[:min_len]

        # Construir prompt
        prompt = build_analysis_prompt(questions, answers)

        # Llamar a Groq API
        response = self._call_groq_api(prompt)

        if not response:
            logger.warning("No se obtuvo respuesta de Groq, usando valores fallback")
            return FALLBACK_VALUES.copy()

        # Parsear respuesta JSON
        result = self._parse_json_response(response)

        if not result:
            logger.warning("No se pudo parsear respuesta, usando valores fallback")
            return FALLBACK_VALUES.copy()

        # Validar y limpiar
        result = self._validate_and_clean_result(result)

        logger.info("Análisis completado exitosamente")
        return result

    def analyze_audio(
        self,
        audio_files: List[Union[str, Path]],
        questions: Optional[List[str]] = None,
        language: str = "es"
    ) -> Dict:
        """
        Analiza respuestas de audio del candidato.

        Args:
            audio_files: Lista de rutas a archivos de audio
            questions: Lista de preguntas (opcional)
            language: Código de idioma para transcripción

        Returns:
            Dict con análisis estructurado + transcripciones
        """
        logger.info(f"Transcribiendo {len(audio_files)} archivos de audio...")

        # Transcribir audios
        answers = self.audio_processor.extract_answers_from_audio(
            audio_files,
            language=language
        )

        # Analizar respuestas transcritas
        result = self.analyze_answers(answers, questions)

        # Agregar transcripciones al resultado
        result["transcriptions"] = answers
        result["audio_processed"] = True

        return result

    def run(self, answers: List[str], questions: Optional[List[str]] = None) -> Dict:
        """
        Método principal de la herramienta MCP.
        Punto de entrada para integración con FastAPI.

        Args:
            answers: Lista de respuestas del candidato (texto)
            questions: Lista de preguntas (opcional)

        Returns:
            Dict con análisis completo del candidato
        """
        return self.analyze_answers(answers, questions)


# Singleton instance para uso global
_hr_copilot_instance: Optional[HRCopilotTool] = None


def get_hr_copilot(
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile"
) -> HRCopilotTool:
    """
    Obtiene una instancia singleton del HR Copilot Tool.

    Args:
        api_key: Groq API key (opcional)
        model: Modelo de Groq a usar

    Returns:
        Instancia de HRCopilotTool
    """
    global _hr_copilot_instance
    if _hr_copilot_instance is None:
        _hr_copilot_instance = HRCopilotTool(api_key=api_key, model=model)
    return _hr_copilot_instance
