# Contributing – MatchKey

Gracias por contribuir a MatchKey.  
Este documento explica cómo trabajar correctamente con el repositorio.

## 1. Branching model
main → estable
dev-miguel → integración
feature/<nombre> → trabajo individual

## 2. Cómo crear una rama
git checkout -b feature/pablom-ocr-skills

## 3. Commits
- Pequeños, claros, atómicos
- Mensaje: "Añadido OCR básico para PDFs"

## 4. Pull Requests
- Siempre hacia dev-miguel
- Nunca hacia main
- Miguel revisa y hace merge si es correcto

## 5. Estructura de carpetas
Respetar estrictamente la estructura del documento CONTEXTO MAESTRO.

## 6. Estándares de código
- Python 3.11
- Black formatting
- Nombres en inglés
- No cambiar nombres de archivos

## 7. Docker
No modificar docker-compose salvo coordinación con Miguel.
