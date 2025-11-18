# backend/app/tests/test_hr_copilot.py

"""
Tests para HR Copilot Tool.
Valida el análisis de respuestas y la extracción de insights.
"""

import json
import pytest
from pathlib import Path
from typing import Dict

from app.services.hr_copilot.hr_copilot_tool import HRCopilotTool
from app.services.hr_copilot.questions import get_questions_text
from app.services.hr_copilot.prompt_templates import FALLBACK_VALUES


# Path to test data
DATA_DIR = Path(__file__).parent.parent / "services" / "hr_copilot" / "data"


def load_test_case(filename: str) -> Dict:
    """Carga un caso de prueba desde JSON"""
    filepath = DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_result_structure(result: Dict) -> None:
    """Valida que el resultado tenga la estructura correcta"""
    assert "motivaciones" in result
    assert "experiencia_clave" in result
    assert "valores_detectados" in result
    assert "soft_skills" in result
    assert "preferencias_equipo" in result
    assert "resumen_psicologico" in result

    assert isinstance(result["motivaciones"], str)
    assert isinstance(result["experiencia_clave"], list)
    assert isinstance(result["valores_detectados"], list)
    assert isinstance(result["soft_skills"], list)
    assert isinstance(result["preferencias_equipo"], str)
    assert isinstance(result["resumen_psicologico"], str)

    assert len(result["motivaciones"]) > 0
    assert len(result["experiencia_clave"]) > 0
    assert len(result["valores_detectados"]) > 0
    assert len(result["soft_skills"]) > 0
    assert len(result["preferencias_equipo"]) > 0
    assert len(result["resumen_psicologico"]) > 0


class TestHRCopilotBasic:
    """Tests básicos de estructura y fallback"""

    def test_initialization(self):
        """Test que la herramienta se inicializa correctamente"""
        hr = HRCopilotTool()
        assert hr is not None
        assert hr.model is not None
        assert hr.audio_processor is not None

    def test_empty_answers_returns_fallback(self):
        """Test que respuestas vacías devuelven valores fallback"""
        hr = HRCopilotTool()
        result = hr.run([])

        validate_result_structure(result)
        # Debería usar fallback
        assert result == FALLBACK_VALUES

    def test_result_structure_with_dummy_data(self):
        """Test estructura del resultado con datos dummy"""
        hr = HRCopilotTool()
        dummy_answers = [
            "Me motiva aprender",
            "Proyecto de universidad",
            "Equipos pequeños",
            "Colaboración",
            "Mantengo la calma"
        ]

        result = hr.run(dummy_answers)
        validate_result_structure(result)


class TestHRCopilotWithRealAPI:
    """
    Tests con llamadas reales a Groq API.
    Requieren GROQ_API_KEY configurada.
    Se marcan como skip si no está disponible.
    """

    @pytest.fixture
    def hr_copilot(self):
        """Fixture que crea instancia de HRCopilotTool"""
        import os
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            pytest.skip("GROQ_API_KEY no configurada")
        return HRCopilotTool(api_key=api_key)

    def test_analyze_junior_developer(self, hr_copilot):
        """Test análisis de candidato junior"""
        test_case = load_test_case("answers_example_1.json")

        result = hr_copilot.run(
            answers=test_case["answers"],
            questions=test_case["questions"]
        )

        validate_result_structure(result)

        # Validar que se detectaron insights relevantes
        expected = test_case["expected_insights"]

        # Al menos algunos valores esperados deben estar
        valores_lower = [v.lower() for v in result["valores_detectados"]]
        assert any(v in valores_lower for v in expected["valores"])

        # Al menos algunas soft skills esperadas
        skills_lower = [s.lower() for s in result["soft_skills"]]
        assert any(s in skills_lower for s in expected["soft_skills"])

        print("\n=== Resultado Junior Developer ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    def test_analyze_senior_pm(self, hr_copilot):
        """Test análisis de candidata senior PM"""
        test_case = load_test_case("answers_example_2.json")

        result = hr_copilot.run(
            answers=test_case["answers"],
            questions=test_case["questions"]
        )

        validate_result_structure(result)

        expected = test_case["expected_insights"]

        # Validar insights
        valores_lower = [v.lower() for v in result["valores_detectados"]]
        assert any(v in valores_lower for v in expected["valores"])

        skills_lower = [s.lower() for s in result["soft_skills"]]
        assert any(s in skills_lower for s in expected["soft_skills"])

        # PM senior debería mostrar liderazgo
        assert "liderazgo" in skills_lower or "lider" in result["resumen_psicologico"].lower()

        print("\n=== Resultado Senior PM ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    def test_analyze_mid_data_scientist(self, hr_copilot):
        """Test análisis de candidato mid-level data scientist"""
        test_case = load_test_case("answers_example_3.json")

        result = hr_copilot.run(
            answers=test_case["answers"],
            questions=test_case["questions"]
        )

        validate_result_structure(result)

        expected = test_case["expected_insights"]

        valores_lower = [v.lower() for v in result["valores_detectados"]]
        assert any(v in valores_lower for v in expected["valores"])

        print("\n=== Resultado Mid-Level Data Scientist ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    def test_all_examples_consistency(self, hr_copilot):
        """Test que todos los ejemplos producen resultados consistentes"""
        examples = [
            "answers_example_1.json",
            "answers_example_2.json",
            "answers_example_3.json"
        ]

        for example_file in examples:
            test_case = load_test_case(example_file)
            result = hr_copilot.run(
                answers=test_case["answers"],
                questions=test_case["questions"]
            )

            validate_result_structure(result)

            # Validar límites razonables
            assert len(result["valores_detectados"]) <= 8
            assert len(result["soft_skills"]) <= 10
            assert len(result["experiencia_clave"]) <= 6
            assert len(result["motivaciones"]) <= 1000
            assert len(result["preferencias_equipo"]) <= 500
            assert len(result["resumen_psicologico"]) <= 1000


class TestHRCopilotValidation:
    """Tests de validación y limpieza de datos"""

    def test_normalize_valores(self):
        """Test normalización de valores con espacios y mayúsculas"""
        hr = HRCopilotTool()

        # Simular datos con formato incorrecto
        data = {
            "motivaciones": "Test",
            "experiencia_clave": ["exp1"],
            "valores_detectados": ["Innovación", "Impacto Social", "ÉTICA"],
            "soft_skills": ["Comunicación Efectiva", "trabajo-equipo"],
            "preferencias_equipo": "Test",
            "resumen_psicologico": "Test"
        }

        cleaned = hr._validate_and_clean_result(data)

        # Valores deben estar normalizados
        assert "innovación" in cleaned["valores_detectados"] or "innovacion" in cleaned["valores_detectados"]
        assert all("_" in v or v.islower() for v in cleaned["valores_detectados"])
        assert all("_" in s or s.islower() for s in cleaned["soft_skills"])

    def test_length_limits(self):
        """Test que se respetan límites de longitud"""
        hr = HRCopilotTool()

        data = {
            "motivaciones": "a" * 2000,  # Muy largo
            "experiencia_clave": [f"exp{i}" for i in range(20)],  # Muchas experiencias
            "valores_detectados": [f"valor{i}" for i in range(15)],  # Muchos valores
            "soft_skills": [f"skill{i}" for i in range(20)],  # Muchas skills
            "preferencias_equipo": "b" * 1000,  # Muy largo
            "resumen_psicologico": "c" * 2000  # Muy largo
        }

        cleaned = hr._validate_and_clean_result(data)

        assert len(cleaned["motivaciones"]) <= 1000
        assert len(cleaned["preferencias_equipo"]) <= 500
        assert len(cleaned["resumen_psicologico"]) <= 1000
        assert len(cleaned["experiencia_clave"]) <= 6
        assert len(cleaned["valores_detectados"]) <= 8
        assert len(cleaned["soft_skills"]) <= 10


def test_questions_consistency():
    """Test que las preguntas estándar son consistentes"""
    questions = get_questions_text()

    assert len(questions) == 5
    assert all(isinstance(q, str) for q in questions)
    assert all(len(q) > 10 for q in questions)


if __name__ == "__main__":
    # Ejecutar tests básicos sin pytest
    print("=== Ejecutando tests básicos ===\n")

    # Test 1: Inicialización
    print("Test 1: Inicialización...")
    hr = HRCopilotTool()
    print("✓ HRCopilotTool inicializado correctamente\n")

    # Test 2: Estructura con datos dummy
    print("Test 2: Estructura con datos dummy...")
    dummy_answers = [
        "Me motiva aprender y crecer",
        "Proyecto de universidad sobre IA",
        "Equipos pequeños y colaborativos",
        "Colaboración y transparencia",
        "Mantengo la calma y analizo"
    ]
    result = hr.run(dummy_answers)
    validate_result_structure(result)
    print("✓ Estructura válida\n")
    print("Resultado:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== Tests completados ===")
    print("Para tests completos con Groq API, ejecuta: pytest test_hr_copilot.py -v")

