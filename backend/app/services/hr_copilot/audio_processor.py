# backend/app/services/hr_copilot/audio_processor.py

"""
Procesador de audio que convierte grabaciones de voz a texto usando Whisper.
Utilizado para transcribir respuestas habladas del candidato.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union
import whisper
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Procesa archivos de audio y los convierte a texto usando Whisper.
    """

    def __init__(self, model_size: str = "base"):
        """
        Inicializa el procesador de audio.

        Args:
            model_size: Tamaño del modelo Whisper (tiny, base, small, medium, large)
                       - tiny: Más rápido, menos preciso (~1GB RAM)
                       - base: Balance recomendado (~1GB RAM)
                       - small: Mejor precisión (~2GB RAM)
                       - medium: Alta precisión (~5GB RAM)
                       - large: Máxima precisión (~10GB RAM)
        """
        self.model_size = model_size
        self._model = None
        logger.info(f"AudioProcessor inicializado con modelo: {model_size}")

    @property
    def model(self):
        """Lazy loading del modelo Whisper"""
        if self._model is None:
            logger.info(f"Cargando modelo Whisper '{self.model_size}'...")
            self._model = whisper.load_model(self.model_size)
            logger.info("Modelo Whisper cargado exitosamente")
        return self._model

    def transcribe_audio(
        self,
        audio_path: Union[str, Path],
        language: str = "es",
        task: str = "transcribe"
    ) -> dict:
        """
        Transcribe un archivo de audio a texto.

        Args:
            audio_path: Ruta al archivo de audio (mp3, wav, m4a, etc.)
            language: Código de idioma ISO 639-1 (es=español, en=inglés)
            task: "transcribe" o "translate" (traducir a inglés)

        Returns:
            dict con:
                - text: Texto transcrito completo
                - segments: Lista de segmentos con timestamps
                - language: Idioma detectado
                - success: bool indicando si fue exitoso
                - error: mensaje de error si falló
        """
        try:
            audio_path = Path(audio_path)

            if not audio_path.exists():
                raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

            logger.info(f"Transcribiendo audio: {audio_path.name}")

            # Transcribir con Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                task=task,
                verbose=False
            )

            logger.info(f"Transcripción completada. Texto de {len(result['text'])} caracteres")

            return {
                "text": result["text"].strip(),
                "segments": result.get("segments", []),
                "language": result.get("language", language),
                "success": True,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error transcribiendo audio: {str(e)}")
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": str(e)
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

