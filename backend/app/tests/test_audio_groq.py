# backend/app/tests/test_audio_groq.py

"""
Tests para AudioProcessor con Groq Whisper API.
Valida la transcripción de audio usando el servicio remoto de Groq.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.services.hr_copilot.audio_processor import AudioProcessor


class TestAudioProcessorGroq:
    """Tests para AudioProcessor con Groq API"""

    def test_initialization_without_api_key(self):
        """Test que AudioProcessor se inicializa sin API key (modo degradado)"""
        with patch.dict(os.environ, {}, clear=True):
            processor = AudioProcessor()
            assert processor is not None
            assert processor.client is None
            assert processor.model == "whisper-large-v3-turbo"

    def test_initialization_with_api_key(self):
        """Test que AudioProcessor se inicializa correctamente con API key"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()
            assert processor is not None
            assert processor.client is not None
            assert processor.api_key == "test_key"

    def test_transcribe_without_client(self):
        """Test que transcribe_audio falla correctamente sin cliente"""
        with patch.dict(os.environ, {}, clear=True):
            processor = AudioProcessor()

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(b"fake audio data")
                tmp_path = tmp.name

            try:
                result = processor.transcribe_audio(tmp_path)

                assert result["success"] is False
                assert "GROQ_API_KEY" in result["error"]
                assert result["text"] == ""
            finally:
                os.unlink(tmp_path)

    def test_transcribe_file_not_found(self):
        """Test que transcribe_audio maneja archivos no encontrados"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            result = processor.transcribe_audio("/nonexistent/file.wav")

            assert result["success"] is False
            assert "no encontrado" in result["error"].lower()
            assert result["text"] == ""

    @patch('app.services.hr_copilot.audio_processor.Groq')
    def test_transcribe_success(self, mock_groq_class):
        """Test transcripción exitosa con Groq API (mock)"""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_transcription = Mock()
        mock_transcription.text = "Esta es una transcripción de prueba"

        mock_client.audio.transcriptions.create.return_value = mock_transcription

        # Inicializar processor
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(b"fake audio data")
                tmp_path = tmp.name

            try:
                result = processor.transcribe_audio(tmp_path, language="es")

                # Verificar resultado
                assert result["success"] is True
                assert result["text"] == "Esta es una transcripción de prueba"
                assert result["error"] is None
                assert result["language"] == "es"

                # Verificar que se llamó a la API correctamente
                mock_client.audio.transcriptions.create.assert_called_once()
                call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
                assert call_kwargs["model"] == "whisper-large-v3-turbo"
                assert call_kwargs["language"] == "es"
                assert call_kwargs["temperature"] == 0.0
            finally:
                os.unlink(tmp_path)

    @patch('app.services.hr_copilot.audio_processor.Groq')
    def test_transcribe_api_error(self, mock_groq_class):
        """Test manejo de errores de API de Groq"""
        # Setup mock para lanzar excepción
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(b"fake audio data")
                tmp_path = tmp.name

            try:
                result = processor.transcribe_audio(tmp_path)

                assert result["success"] is False
                assert "API Error" in result["error"]
                assert result["text"] == ""
            finally:
                os.unlink(tmp_path)

    @patch('app.services.hr_copilot.audio_processor.Groq')
    def test_transcribe_from_bytes(self, mock_groq_class):
        """Test transcripción desde bytes"""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_transcription = Mock()
        mock_transcription.text = "Transcripción desde bytes"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            audio_bytes = b"fake audio data"
            result = processor.transcribe_from_bytes(audio_bytes, "wav", "es")

            assert result["success"] is True
            assert result["text"] == "Transcripción desde bytes"

    @patch('app.services.hr_copilot.audio_processor.Groq')
    def test_transcribe_multiple(self, mock_groq_class):
        """Test transcripción de múltiples archivos"""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        # Mock diferentes respuestas para cada archivo
        transcriptions = [
            "Primera respuesta",
            "Segunda respuesta",
            "Tercera respuesta"
        ]

        mock_client.audio.transcriptions.create.side_effect = [
            Mock(text=text) for text in transcriptions
        ]

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            # Crear archivos temporales
            temp_files = []
            for i in range(3):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(f"audio data {i}".encode())
                    temp_files.append(tmp.name)

            try:
                results = processor.transcribe_multiple(temp_files, language="es")

                assert len(results) == 3
                for i, result in enumerate(results):
                    assert result["success"] is True
                    assert result["text"] == transcriptions[i]
            finally:
                for tmp_path in temp_files:
                    os.unlink(tmp_path)

    @patch('app.services.hr_copilot.audio_processor.Groq')
    def test_extract_answers_from_audio(self, mock_groq_class):
        """Test extracción de respuestas desde audio"""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_transcription = Mock()
        mock_transcription.text = "Respuesta de prueba"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            processor = AudioProcessor()

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(b"fake audio data")
                temp_files = [tmp.name]

            try:
                answers = processor.extract_answers_from_audio(temp_files, language="es")

                assert len(answers) == 1
                assert answers[0] == "Respuesta de prueba"
            finally:
                for tmp_path in temp_files:
                    os.unlink(tmp_path)

    def test_model_size_property(self):
        """Test propiedad model_size para retrocompatibilidad"""
        processor = AudioProcessor(model="whisper-large-v3")
        assert processor.model_size == "whisper-large-v3"


class TestAudioProcessorIntegration:
    """
    Tests de integración con Groq API real.
    Requieren GROQ_API_KEY configurada.
    Se marcan como skip si no está disponible.
    """

    @pytest.fixture
    def processor(self):
        """Fixture que crea AudioProcessor con API key real"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            pytest.skip("GROQ_API_KEY no configurada para tests de integración")
        return AudioProcessor(api_key=api_key)

    @pytest.mark.integration
    def test_transcribe_real_audio(self, processor):
        """
        Test transcripción con audio real.
        NOTA: Este test requiere un archivo de audio real.
        Se skip si no está disponible.
        """
        # Path a archivo de audio de prueba
        test_audio = Path(__file__).parent / "data" / "test_audio.wav"

        if not test_audio.exists():
            pytest.skip("Archivo de audio de prueba no encontrado")

        result = processor.transcribe_audio(test_audio, language="es")

        assert result["success"] is True
        assert len(result["text"]) > 0
        print(f"\nTranscripción: {result['text']}")


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "-s"])

