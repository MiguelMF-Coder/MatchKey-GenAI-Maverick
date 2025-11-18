#!/usr/bin/env python3
# backend/app/services/hr_copilot/test_local.py

"""
Script para probar el HR Copilot localmente sin levantar el servidor.
Útil para desarrollo y debugging.
"""

import sys
import json
from pathlib import Path

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.hr_copilot.hr_copilot_tool import HRCopilotTool
from app.services.hr_copilot.questions import get_questions_text


def test_with_example(example_file: str):
    """Prueba con un archivo de ejemplo"""

    print(f"\n{'='*80}")
    print(f"PROBANDO: {example_file}")
    print(f"{'='*80}\n")

    # Cargar datos de ejemplo
    data_path = Path(__file__).parent / "data" / example_file
    with open(data_path, 'r', encoding='utf-8') as f:
        test_case = json.load(f)

    print(f"Caso: {test_case['test_case']}")
    print(f"Descripción: {test_case['description']}\n")

    # Inicializar HR Copilot
    print("Inicializando HR Copilot...")
    hr = HRCopilotTool()

    # Analizar respuestas
    print("Analizando respuestas...\n")
    result = hr.run(
        answers=test_case["answers"],
        questions=test_case["questions"]
    )

    # Mostrar resultados
    print(f"\n{'─'*80}")
    print("RESULTADOS DEL ANÁLISIS:")
    print(f"{'─'*80}\n")

    print("📌 MOTIVACIONES:")
    print(f"   {result['motivaciones']}\n")

    print("💼 EXPERIENCIA CLAVE:")
    for exp in result['experiencia_clave']:
        print(f"   • {exp}")
    print()

    print("⭐ VALORES DETECTADOS:")
    print(f"   {', '.join(result['valores_detectados'])}\n")

    print("🎯 SOFT SKILLS:")
    print(f"   {', '.join(result['soft_skills'])}\n")

    print("👥 PREFERENCIAS DE EQUIPO:")
    print(f"   {result['preferencias_equipo']}\n")

    print("🧠 RESUMEN PSICOLÓGICO:")
    print(f"   {result['resumen_psicologico']}\n")

    # Comparar con esperado (si existe)
    if "expected_insights" in test_case:
        print(f"\n{'─'*80}")
        print("COMPARACIÓN CON ESPERADO:")
        print(f"{'─'*80}\n")

        expected = test_case["expected_insights"]

        # Valores
        valores_lower = [v.lower() for v in result['valores_detectados']]
        valores_match = [v for v in expected.get("valores", []) if v.lower() in valores_lower]
        print(f"✓ Valores coincidentes: {', '.join(valores_match) if valores_match else 'Ninguno'}")

        # Skills
        skills_lower = [s.lower() for s in result['soft_skills']]
        skills_match = [s for s in expected.get("soft_skills", []) if s.lower() in skills_lower]
        print(f"✓ Skills coincidentes: {', '.join(skills_match) if skills_match else 'Ninguno'}")

    print(f"\n{'='*80}\n")

    return result


def test_quick():
    """Test rápido con respuestas cortas"""

    print(f"\n{'='*80}")
    print("TEST RÁPIDO CON RESPUESTAS SIMPLES")
    print(f"{'='*80}\n")

    hr = HRCopilotTool()

    answers = [
        "Me motiva aprender tecnologías nuevas y trabajar en equipo en proyectos desafiantes.",
        "Mi proyecto más importante fue desarrollar una aplicación web para gestión de inventarios. Aprendí mucho sobre bases de datos y diseño de interfaces.",
        "Trabajo mejor en equipos pequeños donde hay buena comunicación y se fomenta la colaboración.",
        "Valoro mucho la honestidad y la ética en el trabajo. También me importa el aprendizaje continuo.",
        "Cuando hay presión, trato de mantener la calma, priorizar tareas y pedir ayuda si la necesito."
    ]

    result = hr.run(answers)

    print("RESULTADO:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n{'='*80}\n")

    return result


def main():
    """Función principal"""

    import os
    from dotenv import load_dotenv

    # Cargar variables de entorno
    load_dotenv()

    # Verificar API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n⚠️  ADVERTENCIA: GROQ_API_KEY no configurada")
        print("   El análisis usará valores fallback (dummy)")
        print("   Para usar análisis real, configura tu API key en .env\n")
        input("Presiona Enter para continuar...")

    print("\n" + "="*80)
    print(" "*20 + "HR COPILOT - TEST LOCAL")
    print("="*80)

    # Menú
    while True:
        print("\nOpciones:")
        print("  1. Test con Candidato Junior (ejemplo 1)")
        print("  2. Test con Candidata Senior PM (ejemplo 2)")
        print("  3. Test con Candidato Mid-Level (ejemplo 3)")
        print("  4. Test rápido con respuestas simples")
        print("  5. Probar todos los ejemplos")
        print("  0. Salir")

        choice = input("\nSelecciona una opción: ").strip()

        if choice == "0":
            print("\n¡Hasta luego! 👋\n")
            break
        elif choice == "1":
            test_with_example("answers_example_1.json")
        elif choice == "2":
            test_with_example("answers_example_2.json")
        elif choice == "3":
            test_with_example("answers_example_3.json")
        elif choice == "4":
            test_quick()
        elif choice == "5":
            test_with_example("answers_example_1.json")
            test_with_example("answers_example_2.json")
            test_with_example("answers_example_3.json")
        else:
            print("\n❌ Opción inválida\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()

