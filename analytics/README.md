# Capa Analítica — TFG MatchKey (Business Analytics, UFV)

> Documento triple: **(A) reproducibilidad técnica**, **(B) índice de trazabilidad** para la memoria y
> **(C) chuleta de defensa**. Autor: Miguel Martínez Fernández · Convocatoria: extraordinaria (julio 2026).

---

## 1. Qué es esto

La **capa analítica (offline)** del TFG MatchKey. Toma los datos de producción de la plataforma
(generados por scraping/OCR) y los analiza para responder a los objetivos del anteproyecto (OE1–OE5)
con **outputs auditables** (CSVs, figuras, notebooks ejecutables).

- **NO toca `backend/` ni `frontend/`.** No modifica modelos, routers ni la base de datos.
- Vive en: `analytics/` (scripts), `notebooks/` (01–05), `data/` (entradas y salidas planas).
- Todo es **reproducible** desde cero y **trazable** a un objetivo del TFG.

---

## 2. Cómo reproducir (orden exacto)

### Entorno
- **Python 3.12** en un entorno virtual del repo: `.venv/`
- Dependencias: [`requirements-analytics.txt`](../requirements-analytics.txt) (pandas, scikit-learn, scipy, matplotlib, seaborn, plotly, jupyter).

```bash
# (una vez) crear venv e instalar dependencias
py -V:3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-analytics.txt
.venv\Scripts\python.exe -m ipykernel install --user --name matchkey-tfg --display-name "Python (MatchKey TFG)"
```

### Paso 1 — Export de datos de producción → `data/matchkey/`
```bash
.venv\Scripts\python.exe analytics\export_data.py
```
Lee los **JSON fuente** del scraping/OCR y genera CSVs planos.

### Paso 2 — Integración ESCO → `data/esco/`
```bash
.venv\Scripts\python.exe data\esco\download_esco.py     # cosecha la taxonomía ESCO vía API oficial
.venv\Scripts\python.exe analytics\esco_mapper.py        # mapea skills/categorías MatchKey -> ESCO
```

### Paso 3 — Notebooks `01 → 05` (en orden)
Abrir en Jupyter/VSCode con el kernel **"Python (MatchKey TFG)"**, o ejecutar en lote:
```bash
.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\01_ingenieria_dato.ipynb
.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\02_clustering.ipynb
.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\03_tfidf_matching.ipynb
.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\04_clasificacion.ipynb
.venv\Scripts\python.exe -m nbconvert --to notebook --execute --inplace notebooks\05_negocio.ipynb
```
El **01** debe ir primero (genera `data/clean/`, del que dependen 02–05).

### ⚠️ Nota sobre la fuente de verdad
Las **skills de cada vacante** se toman de los **arrays de los JSON** (`skills_must`, `skills_nice`,
`tech_stack`, `soft_skills`, `languages`), **NO de la tabla `job_skills` de la base de datos**: las 236
vacantes se siembran directamente desde `jobs_final.json` y nunca rellenan esa tabla (queda vacía). Por eso
el análisis parte del export plano y no de la BD.

---

## 3. Trazabilidad OE → notebook → output → evidencia

Redacción **literal del anteproyecto** y reasignación corregida (I1→OE1, I3→OE2, I4→OE3, I2→OE4, I5→OE5):

| OE | Objetivo (anteproyecto) | Notebook | Output principal | Evidencia / cifra |
|----|-------------------------|----------|------------------|-------------------|
| **OE1** | Cuantificar el desajuste entre las competencias que ofrecen los candidatos y las que demandan las vacantes, identificando qué competencias concretas presentan mayor brecha. | `05_negocio.ipynb` §1 | `data/clean/skill_gap_analysis.csv`, `notebooks/figures/05_skill_gaps.png` | Top gaps de *tools* (AWS, Node.js, Azure, PostgreSQL…), oferta ajustada ≈0% |
| **OE2** | Evaluar si un enfoque de recuperación de información (TF-IDF y similitud del coseno) aporta valor sobre el sistema de matching heurístico vigente, y precisar en qué aspecto lo hace. | `03_tfidf_matching.ipynb` | `data/clean/model2_ranking_comparison.csv`, `notebooks/figures/03_tfidf_vs_heuristico.png` | Spearman **0.292**; `values_fit`/`team_fit` **constantes (60)**; TF-IDF recupera skills citadas en la prosa |
| **OE3** | Determinar si las categorías de vacante disponibles permiten segmentar adecuadamente la oferta de empleo, o si se requiere un enfoque alternativo de clasificación. | `04_clasificacion.ipynb` | `data/validation/manual_validation_resultado.csv`, `notebooks/figures/04_confusion_matrix.png`, `04_manual_vs_llm.png` | macro-F1 **0.42** vs baseline **0.15**; **Kappa 0.553 (moderado)**; **ML/DS F1=0** (absorbidas por AI) |
| **OE4** | Evaluar el grado de diferenciación entre los perfiles de los candidatos, para valorar la viabilidad de un emparejamiento de perfiles complementarios (co-teaching). | `02_clustering.ipynb` | `data/clean/model1_representaciones_comparativa.csv`, `data/clean/candidate_clusters.csv`, `notebooks/figures/02_pca_3reps.png` | silhouette **0.104** (mejor de 3 reps, todas <0.2) → talento homogéneo → co-teaching poco viable |
| **OE5** | Identificar oportunidades concretas de cierre de la brecha de competencias mediante recomendación de formación, conectando cada carencia con un recurso formativo real. | `05_negocio.ipynb` §2 | `data/clean/gap_to_courses.csv` | **6/15** gaps de *tool* enlazados a un curso real (nombre+URL); resto sin curso (honesto) |

*(El notebook `01_ingenieria_dato.ipynb` es **transversal**: inventario, diccionario, limpieza y auditoría de
los datos que usan todos los OE. Salidas en `data/clean/`.)*

---

## 4. Resultados clave (cifras)

- **Modelo 1 — Clustering (OE4):** se comparan 3 representaciones del candidato (skills_only, enriquecida,
  tfidf_text+SVD) con **silhouette coseno** (misma métrica en las tres). Principal = `tfidf_text`,
  **silhouette = 0.104**; las **tres por debajo de 0.2** → **talento homogéneo**, sin segmentación fuerte
  (resultado válido, no se fuerza interpretación) → co-teaching de perfiles complementarios poco viable.
- **Modelo 2 — TF-IDF vs heurístico (OE2):** **Spearman = 0.292** (acuerdo parcial); `overlap@5 = 0.086`,
  `overlap@10 = 0.116`. Demostrado que **`values_fit` y `team_fit` son constantes (60)** en estos datos →
  el ranking heurístico depende **solo de `skills_fit`**. TF-IDF aporta al usar el **texto completo** de la oferta.
- **Modelo 3 — Clasificación `category_llm` (OE3):** **macro-F1 = 0.42** vs **baseline 0.15** (CV estratificada
  5-fold, TF-IDF dentro del Pipeline → sin *data leakage*). **Validación manual:** acuerdo bruto 66.7%,
  **Cohen's Kappa = 0.553 (moderado)**. **ML y Data Science con F1 = 0** (absorbidas por AI); el desacuerdo
  humano se concentra en la frontera **AI/Data Science/Software Engineering** → las categorías **no segmentan bien**.
- **Gap analysis (OE1/OE5):** los gaps reales son **tools** que el *pool* no tiene (AWS, Node.js, JavaScript,
  Azure, PostgreSQL, MySQL + tooling de automatización IA). Corregido el **artefacto de idioma** (soft skills
  ES↔EN). **6/15** gaps de *tool* tienen un curso real asociado en el catálogo.

---

## 5. Honestidad declarada (leer antes de interpretar)

**Ningún componente dummy/stub se presenta como resultado analítico.** Se auditan y se nombran como tales:

- **`category_llm` es *silver-standard***: etiqueta generada por un LLM leyendo la oferta, no anotación humana.
  Entrenar sobre el mismo texto para predecirla es **circular** → el macro-F1 mide *consistencia*, no *validez*;
  la validez la aporta la **validación manual (Kappa)**, no el F1.
- **Componentes dummy/heurísticos del backend** (auditados en los notebooks, no usados como resultado):
  - `skills_extractor` → diccionario base mínimo (no es un extractor real).
  - `HR Copilot` → salida placeholder.
  - `values_fit` / `team_fit` (matching) → **heurísticos/constantes** (60) con los datos sembrados.
- **Muestra pequeña** (100 candidatos, 236 vacantes) → resultados **exploratorios**, no inferencia poblacional;
  se prioriza CV estratificada, macro-F1 y reporte honesto de clases inviables (excluidas las < 8 ejemplos).
- **Cobertura ESCO ≈ 13%** de las skills de MatchKey (86.6% sin correspondencia). Causa doble y **documentada
  como hallazgo**: (1) tools/librerías modernas no existen en ESCO (taxonomía más gruesa) y (2) soft skills en
  español vs ESCO en inglés (gap multilingüe). No es un fallo del método.

---

## 6. Inventario de outputs (qué genera cada paso, con su ruta)

### `analytics/export_data.py` → `data/matchkey/`
- `candidates.csv`, `candidate_skills.csv`, `candidate_education.csv`, `candidate_languages.csv`
- `vacantes.csv`, `job_skills.csv`, `courses.csv`, `companies.csv`, `_export_summary.csv`

### `data/esco/download_esco.py` → `data/esco/`
- `skills_en.csv` (13.485 skills), `occupations_en.csv` (2.942 ocupaciones), `_esco_meta.json`

### `analytics/esco_mapper.py` → `data/esco/`
- `matchkey_skills_to_esco.csv`, `matchkey_categories_to_esco_occupations.csv`, `_coverage_summary.csv`

### `notebooks/01_ingenieria_dato.ipynb`
- `data/clean/`: `_diccionario_variables.csv`, `candidates_clean.csv`, `vacantes_clean.csv`,
  `candidate_skills_clean.csv`, `job_skills_clean.csv`
- `notebooks/figures/`: `01_vacantes_nulos.png`, `01_category_llm.png`, `01_candidatos_dist.png`,
  `01_cursos_categorias.png`, `01_skills_demandadas.png`

### `notebooks/02_clustering.ipynb`
- `data/clean/`: `model1_representaciones_comparativa.csv`, `candidate_clusters.csv`
- `notebooks/figures/`: `02_seleccion_k_3reps.png`, `02_pca_3reps.png`

### `notebooks/03_tfidf_matching.ipynb`
- `data/clean/`: `model2_ranking_comparison.csv`
- `notebooks/figures/`: `03_tfidf_vs_heuristico.png`

### `notebooks/04_clasificacion.ipynb`
- `data/validation/`: `manual_validation_template.csv` (se crea si no existe; **no se sobrescribe** si está rellena),
  `manual_validation_resultado.csv`, y `notas_cualitativas.csv` *(solo si la plantilla tiene columna `notas`)*
- `notebooks/figures/`: `04_confusion_matrix.png`, `04_manual_vs_llm.png`

### `notebooks/05_negocio.ipynb`
- `data/clean/`: `skill_gap_analysis.csv`, `gap_to_courses.csv`
- `notebooks/figures/`: `05_skill_gaps.png`

---

## Pendiente
- Añadir la columna `notas` (anotaciones del autor sobre vacantes de categoría discutible) a
  `data/validation/manual_validation_template.csv` y re-ejecutar `04` → genera `notas_cualitativas.csv`
  como evidencia cualitativa de la ambigüedad de la taxonomía (OE3).
