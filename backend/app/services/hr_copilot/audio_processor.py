# backend/app/services/hr_copilot/audio_processor.py

"""
Procesador de audio que convierte grabaciones de voz a texto usando Groq Whisper API.
Utilizado para transcribir respuestas habladas del candidato.
Usa whisper-large-v3-turbo de Groq para transcripción rápida y precisa.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Procesa archivos de audio y los convierte a texto usando Groq Whisper API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-large-v3-turbo"
    ):
        """
        Inicializa el procesador de audio con Groq API.

        Args:
            api_key: Groq API key (si no se provee, se lee de GROQ_API_KEY env var)
            model: Modelo de Groq Whisper a usar:
                   - whisper-large-v3-turbo: Muy rápido, excelente precisión (recomendado)
                   - whisper-large-v3: Rápido, máxima precisión
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model

        if not self.api_key:
            logger.warning(
                "GROQ_API_KEY no configurada. La transcripción de audio no funcionará. "
                "Obtén tu API key en: https://console.groq.com/keys"
            )
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"AudioProcessor inicializado con Groq API - Modelo: {model}")

    @property
    def model_size(self):
        """Compatibilidad con código legacy - mapea a nombre de modelo Groq"""
        return self.model

    def transcribe_audio(
        self,
        audio_path: Union[str, Path],
        language: str = "es",
        task: str = "transcribe"
    ) -> dict:
        """
        Transcribe un archivo de audio a texto usando Groq Whisper API.

        Args:
            audio_path: Ruta al archivo de audio (mp3, wav, m4a, etc.)
            language: Código de idioma ISO 639-1 (es=español, en=inglés)
            task: "transcribe" o "translate" (traducir a inglés)

        Returns:
            dict con:
                - text: Texto transcrito completo
                - segments: Lista de segmentos (vacía en API mode)
                - language: Idioma detectado
                - success: bool indicando si fue exitoso
                - error: mensaje de error si falló
        """
        if not self.client:
            logger.error("Cliente Groq no inicializado. Verifica GROQ_API_KEY")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": "GROQ_API_KEY no configurada"
            }

        try:
            audio_path = Path(audio_path)

            if not audio_path.exists():
                raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

            logger.info(f"Transcribiendo audio con Groq API: {audio_path.name}")

            # Transcribir con Groq Whisper API
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language if language != "auto" else None,
                    response_format="verbose_json",  # Include more details
                    temperature=0.0  # Deterministic output
                )

            # Normalizar respuesta de Groq al formato esperado
            text = transcription.text.strip()

            logger.info(f"Transcripción completada. Texto de {len(text)} caracteres")

            return {
                "text": text,
                "segments": [],  # Groq API no devuelve segmentos en el formato actual
                "language": language,
                "success": True,
                "error": None
            }

        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {str(e)}")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": f"Archivo no encontrado: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error transcribiendo audio con Groq API: {str(e)}")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": f"Error de transcripción: {str(e)}"
            }

    def transcribe_multiple(
        self,
        audio_files: list[Union[str, Path]],
        language: str = "es"
    ) -> list[dict]:
        """
        Transcribe múltiples archivos de audio.

        Args:
            audio_files: Lista de rutas a archivos de audio
            language: Código de idioma

        Returns:
            Lista de diccionarios con resultados de transcripción
        """
        results = []
        for audio_file in audio_files:
            result = self.transcribe_audio(audio_file, language)
            results.append(result)

        return results

    def transcribe_from_bytes(
        self,
        audio_bytes: bytes,
        file_extension: str = "wav",
        language: str = "es"
    ) -> dict:
        """
        Transcribe audio desde bytes (útil para uploads HTTP).

        Args:
            audio_bytes: Bytes del archivo de audio
            file_extension: Extensión del archivo (wav, mp3, etc.)
            language: Código de idioma

        Returns:
            dict con resultado de transcripción
        """
        if not self.client:
            logger.error("Cliente Groq no inicializado")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": "GROQ_API_KEY no configurada"
            }

        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_extension}",
                delete=False
            ) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            # Transcribir
            result = self.transcribe_audio(tmp_path, language)

            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass

            return result

        except Exception as e:
            logger.error(f"Error transcribiendo desde bytes: {str(e)}")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": str(e)
            }

    def extract_answers_from_audio(
        self,
        audio_files: list[Union[str, Path]],
        language: str = "es"
    ) -> list[str]:
        """
        Extrae respuestas de texto desde múltiples archivos de audio.
        Útil para procesar respuestas de entrevista grabadas.

        Args:
            audio_files: Lista de archivos de audio (uno por pregunta)
            language: Código de idioma

        Returns:
            Lista de strings con las respuestas transcritas
        """
        results = self.transcribe_multiple(audio_files, language)

        answers = []
        for i, result in enumerate(results, 1):
            if result["success"]:
                answers.append(result["text"])
            else:
                logger.warning(f"Pregunta {i}: Transcripción falló - {result['error']}")
                answers.append("")

        return answers


# Singleton instance (opcional)
_audio_processor_instance: Optional[AudioProcessor] = None


def get_audio_processor(model_size: str = "base") -> AudioProcessor:
    """
    Obtiene una instancia singleton del AudioProcessor.

    Args:
        model_size: Tamaño del modelo Whisper

    Returns:
        Instancia de AudioProcessor
    """
    global _audio_processor_instance
    if _audio_processor_instance is None:
        _audio_processor_instance = AudioProcessor(model_size)
    return _audio_processor_instance

