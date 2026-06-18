# Datos — MatchKey (capa analítica del TFG)

Este directorio contiene los datasets usados por los notebooks de análisis (`notebooks/01`–`05`).

## Naturaleza de los datos
- **Candidatos: dataset SINTÉTICO.** Los 100 perfiles de candidato (incluido `cv_ocr_analizados_100.json` y los CSV derivados) son **ficticios, generados para el proyecto**: nombres, contacto y currículos no corresponden a personas reales. Se usó intencionadamente para no tratar datos personales reales (*privacy by design*).
  - La plataforma incorpora un **pipeline de parsing de CV real y funcional** (Tesseract OCR + pdfplumber/pdf2image + `document_parser` con spaCy) para que, en producción, un usuario suba su CV real; ese pipeline **no se aplicó sobre CVs reales** en este TFG.
- **Vacantes, cursos y empresas:** datos **reales** obtenidos por scraping web (Adzuna y otras fuentes públicas) + enriquecimiento con LLM.
- **`data/esco/`:** taxonomía pública ESCO (Comisión Europea) y los mapeos MatchKey↔ESCO.
- **`data/clean/`:** outputs agregados/derivados del análisis (insights, gaps, métricas de modelos, diccionario, estadísticos).

## Etiquetas silver-standard
`category_llm` (categoría de vacante) y `skills_extractor` (clasificación de skills) fueron **generadas por un LLM**, no por anotación humana ni por el extractor heurístico. Se documentan como tales en la memoria.

## Reproducibilidad
Los notebooks `01`–`05` se ejecutan sobre estos datos (incluidos en el repo) y dejan sus outputs guardados como evidencia. Al ser los candidatos sintéticos, no hay restricción de privacidad para su publicación.
