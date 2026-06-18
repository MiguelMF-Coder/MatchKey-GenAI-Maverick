# Datos — MatchKey (capa analítica del TFG)

Este directorio contiene los datasets usados por los notebooks de análisis (`notebooks/01`–`05`).

## Qué se publica
- `data/esco/` — taxonomía pública ESCO (Comisión Europea) y los mapeos MatchKey↔ESCO.
- `data/clean/` — outputs agregados y derivados del análisis (insights de negocio, gaps, métricas de los modelos, diccionario de variables, estadísticos). Las claves de candidato son **identificadores pseudonimizados** (enteros), sin datos personales.
- `data/matchkey/` — datos de **vacantes, cursos y empresas** (información pública de ofertas y catálogo).

## Qué NO se publica (RGPD)
Por contener **datos personales de candidatos reales** (nombre, email, teléfono, CVs), se excluyen del repositorio público:
- `data/matchkey/candidates.csv`, `candidate_education.csv`, `candidate_languages.csv`
- `data/clean/candidates_clean.csv`
- Los CVs procesados por OCR (`cv_ocr_*.json`)

Estos ficheros están **disponibles bajo petición** al tribunal evaluador, conforme a la sección de ética y privacidad de la memoria. El tratamiento se ha realizado de forma agregada y pseudonimizada en todos los análisis.

## Reproducibilidad
Con los datos no personales incluidos, los notebooks `01`–`05` son ejecutables salvo las partes que requieren los microdatos de candidato (clustering y matching), cuyos **outputs ya quedan guardados** en los notebooks como evidencia.
