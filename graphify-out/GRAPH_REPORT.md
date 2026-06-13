# Graph Report - .  (2026-06-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 494 nodes · 1087 edges · 57 communities (37 shown, 20 thin omitted)
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 403 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f363ced4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Candidate Interview Management|Candidate Interview Management]]
- [[_COMMUNITY_Team and Company Profiles|Team and Company Profiles]]
- [[_COMMUNITY_Course Recommendations Logic|Course Recommendations Logic]]
- [[_COMMUNITY_System Initialization and Health|System Initialization and Health]]
- [[_COMMUNITY_Company Job and Co-Teaching|Company Job and Co-Teaching]]
- [[_COMMUNITY_Company Data and Culture|Company Data and Culture]]
- [[_COMMUNITY_Resume Parsing and Extraction|Resume Parsing and Extraction]]
- [[_COMMUNITY_Candidate Profile and Analytics|Candidate Profile and Analytics]]
- [[_COMMUNITY_Fit Score Calculations|Fit Score Calculations]]
- [[_COMMUNITY_Project Infrastructure and Frontend|Project Infrastructure and Frontend]]
- [[_COMMUNITY_Candidate Job Matching Scores|Candidate Job Matching Scores]]
- [[_COMMUNITY_Matching Engine Algorithms|Matching Engine Algorithms]]
- [[_COMMUNITY_Job Creation and Management|Job Creation and Management]]
- [[_COMMUNITY_Job Application and Matching|Job Application and Matching]]
- [[_COMMUNITY_Core Data Models|Core Data Models]]
- [[_COMMUNITY_Graphify Skill Extraction|Graphify Skill Extraction]]
- [[_COMMUNITY_Course Data Loading|Course Data Loading]]
- [[_COMMUNITY_Text and Skill Extraction|Text and Skill Extraction]]
- [[_COMMUNITY_HR Copilot AI Calls|HR Copilot AI Calls]]
- [[_COMMUNITY_Database Seeding and Routing|Database Seeding and Routing]]
- [[_COMMUNITY_HR Copilot Tool Logic|HR Copilot Tool Logic]]
- [[_COMMUNITY_University Links Extraction|University Links Extraction]]
- [[_COMMUNITY_Course Scraping Adapter|Course Scraping Adapter]]
- [[_COMMUNITY_Candidate Services and UI|Candidate Services and UI]]
- [[_COMMUNITY_MCP Client Stub|MCP Client Stub]]
- [[_COMMUNITY_Web Text Cleaning|Web Text Cleaning]]
- [[_COMMUNITY_Job Description Scraper|Job Description Scraper]]
- [[_COMMUNITY_Candidate Email Notifications|Candidate Email Notifications]]
- [[_COMMUNITY_University Base Info Scraper|University Base Info Scraper]]
- [[_COMMUNITY_University Web Text Cleaning|University Web Text Cleaning]]
- [[_COMMUNITY_Entrypoint Script|Entrypoint Script]]
- [[_COMMUNITY_Backend Main Application|Backend Main Application]]
- [[_COMMUNITY_Company API Routing|Company API Routing]]
- [[_COMMUNITY_Copilot API Routing|Copilot API Routing]]
- [[_COMMUNITY_Matching API Routing|Matching API Routing]]
- [[_COMMUNITY_Frontend Application|Frontend Application]]
- [[_COMMUNITY_MatchKey Project Overview|MatchKey Project Overview]]
- [[_COMMUNITY_Branching Strategy|Branching Strategy]]
- [[_COMMUNITY_Commit Guidelines|Commit Guidelines]]
- [[_COMMUNITY_Docker Modification Guidelines|Docker Modification Guidelines]]
- [[_COMMUNITY_Pull Request Guidelines|Pull Request Guidelines]]
- [[_COMMUNITY_PostgreSQL Admin Service|PostgreSQL Admin Service]]
- [[_COMMUNITY_Getting Started Guide|Getting Started Guide]]

## God Nodes (most connected - your core abstractions)
1. `Job` - 54 edges
2. `User` - 53 edges
3. `Candidate` - 48 edges
4. `CandidateSkill` - 48 edges
5. `Company` - 37 edges
6. `Application` - 29 edges
7. `JobSkill` - 29 edges
8. `TeamProfile` - 27 edges
9. `TeamMember` - 27 edges
10. `CandidateInterview` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Banner vertical branding MatchKey sidebar` --references--> `MatchKey project README`  [INFERRED]
  frontend/images/banner_barra_lateral.png → README.md
- `Banner MatchKey login page` --references--> `MatchKey project README`  [INFERRED]
  frontend/images/banner_inicio_sesion.png → README.md
- `Illustration for candidate home page` --references--> `MatchKey project README`  [INFERRED]
  frontend/images/candidate_home_illustration.png → README.md
- `Illustration for company home page` --references--> `MatchKey project README`  [INFERRED]
  frontend/images/company_home_illustration.png → README.md
- `System prompt template for MatchKey project` --references--> `MatchKey project README`  [INFERRED]
  graphify-out/converted/🟣 PLANTILLA SYSTEM PROMPT_8e503c68.md → README.md

## Import Cycles
- None detected.

## Communities (57 total, 20 thin omitted)

### Community 0 - "Candidate Interview Management"
Cohesion: 0.13
Nodes (44): Path, Session, Any, Session, UploadFile, BaseModel, CandidateInterview, Resultado de una 'Llamada IA' del HR Copilot. (+36 more)

### Community 1 - "Team and Company Profiles"
Cohesion: 0.16
Nodes (42): Session, Session, Session, Base, _guess_team_type(), seed_team_profiles(), Candidate, Company (+34 more)

### Community 2 - "Course Recommendations Logic"
Cohesion: 0.07
Nodes (38): ensure_candidate_id(), fetch_gaps_for_job(), fetch_recommended_courses_for_job(), get_auth_email(), Renderiza la sección de cursos recomendados para la vacante concreta.     Espera, Llama a /candidates/{id}/job/{job}/gaps (GET) para recuperar:     - skills fuert, Llama al endpoint /candidates/{candidate_id}/job/{job_id}/recommended_courses, render() (+30 more)

### Community 3 - "System Initialization and Health"
Cohesion: 0.10
Nodes (22): on_startup(), Company, Job, Session, create_accenture_demo_user(), init_db(), Crea (si no existe) un usuario de empresa demo para Accenture     y lo vincula a, load_json() (+14 more)

### Community 4 - "Company Job and Co-Teaching"
Cohesion: 0.11
Nodes (25): ensure_company_id(), fetch_co_teaching_pairs(), fetch_company_jobs(), fetch_company_profile(), get_auth_email(), Llama a /jobs/{id}/co_teaching (GET) para recuperar las parejas recomendadas., Se asegura de que tengamos un company_id en sesión.     - Si ya existe en sessio, Intenta obtener las vacantes de la empresa a partir del perfil.     Busca claves (+17 more)

### Community 5 - "Company Data and Culture"
Cohesion: 0.20
Nodes (18): Company, Path, Session, Session, get_or_create_company(), load_values_dataset(), seed_companies_from_values_dataset(), upsert_company_culture() (+10 more)

### Community 6 - "Resume Parsing and Extraction"
Cohesion: 0.16
Nodes (7): UploadFile, CVParser, CVReader, parse_cv_upload(), Coge el texto de CVReader, lo entiende y lo devuelve estructurado., Guarda temporalmente el CV subido, lanza CVReader + CVParser     y devuelve un d, Convierte cualquier archivo (PDF, DOCX, IMG) en texto limpio.

### Community 7 - "Candidate Profile and Analytics"
Cohesion: 0.15
Nodes (19): ensure_candidate_id(), extract_scores_from_job(), fetch_candidate_profile(), fetch_recommended_jobs(), get_auth_email(), Llama a /candidates/{id}/profile (GET) para recuperar los datos actuales., Llama a /candidates/{id}/recommended_jobs (GET) para recuperar las vacantes reco, render() (+11 more)

### Community 8 - "Fit Score Calculations"
Cohesion: 0.18
Nodes (18): compute_global_fit(), compute_skills_fit(), compute_team_fit(), compute_values_fit(), _map_autonomy(), _match_ratio(), _most_common_or_none(), _norm() (+10 more)

### Community 9 - "Project Infrastructure and Frontend"
Cohesion: 0.12
Nodes (17): Companies about us URLs dataset, Backend Python requirements, Docker service: backend (FastAPI), Docker service: db (PostgreSQL), Docker service: frontend (Streamlit), Banner vertical branding MatchKey sidebar, Banner MatchKey login page, Illustration for candidate home page (+9 more)

### Community 10 - "Candidate Job Matching Scores"
Cohesion: 0.21
Nodes (13): Candidate, Job, Session, compute_global_fit(), compute_skills_fit(), compute_team_fit(), compute_values_fit(), get_match_scores() (+5 more)

### Community 11 - "Matching Engine Algorithms"
Cohesion: 0.24
Nodes (13): Candidate, Job, compute_global_fit(), compute_skills_fit(), compute_team_fit(), compute_values_fit(), get_match_scores(), _norm() (+5 more)

### Community 12 - "Job Creation and Management"
Cohesion: 0.25
Nodes (13): create_job(), delete_job_backend(), ensure_company_id(), fetch_company_jobs_with_applications(), fetch_job_applications(), get_auth_email(), Se asegura de que tengamos un company_id en sesión.     - Si ya existe en sessio, Crea una vacante en el backend.     - Si hay fichero, se envía como multipart (f (+5 more)

### Community 13 - "Job Application and Matching"
Cohesion: 0.24
Nodes (12): apply_to_job(), ensure_candidate_id(), extract_scores(), fetch_match_scores(), fetch_recommended_jobs(), format_description(), get_auth_email(), 1) Llama a /candidates/{id}/recommended_jobs para sacar las vacantes base.     2 (+4 more)

### Community 14 - "Core Data Models"
Cohesion: 0.36
Nodes (3): Campos de creación y actualización, comunes a casi todas las tablas., TimestampMixin, JobRecommendation

### Community 15 - "Graphify Skill Extraction"
Cohesion: 0.20
Nodes (10): graphify skill, graphify reference: add URL and watch folder, graphify reference: extra exports and benchmark, graphify reference: extraction subagent prompt, graphify reference: GitHub clone and cross-repo merge, graphify reference: commit hook and CLAUDE.md integration, graphify reference: query, path, explain, graphify reference: transcribe video and audio (+2 more)

### Community 16 - "Course Data Loading"
Cohesion: 0.39
Nodes (8): Any, load_courses(), _normalize_text(), Carga el dataset de cursos del scraping SOLO UNA VEZ.     Preprocesa y normaliza, Dado un listado de gaps (skills que faltan), devuelve una lista     de cursos re, recommend_courses_for_gaps(), _similarity(), _split_skills_field()

### Community 17 - "Text and Skill Extraction"
Cohesion: 0.28
Nodes (5): normalize_text(), Limpiar y normalizar texto:     - quitar caracteres raros     - normalizar acent, Por ahora: versión dummy.         Más adelante:         - usar diccionario, Tool de extracción de skills.     Pablo M implementará aquí TF-IDF, embeddings,, SkillsExtractor

### Community 18 - "HR Copilot AI Calls"
Cohesion: 0.39
Nodes (7): call_hr_copilot(), ensure_candidate_id(), get_auth_email(), Reutiliza la lógica de profile.py:     - Si ya tenemos candidate_id en sesión, l, Llama al endpoint del HR Copilot.     Asumimos un contrato tipo:       POST /cop, render(), render_honesty_message()

### Community 19 - "Database Seeding and Routing"
Cohesion: 0.25
Nodes (8): backend/app/db/init_db.py, backend/app/db/seed_candidates_from_ocr.py, backend/app/db/seed_companies_from_values_dataset.py, backend/app/db/seed_fake_applications.py, backend/app/db/seed_jobs_from_scraping.py, backend/app/routers/auth.py, backend/app/routers/jobs.py, frontend/company/co_teaching.py

### Community 20 - "HR Copilot Tool Logic"
Cohesion: 0.33
Nodes (3): HRCopilotTool, # TODO: análisis real. Esto es dummy., Asier: aquí luego podrás llamar a un LLM o usar reglas.     De momento devolvemo

### Community 21 - "University Links Extraction"
Cohesion: 0.38
Nodes (6): extract_links_from_elements(), get_relevant_links(), open_main_menu(), Hace hover sobre los elementos principales del menú para desplegar submenús, Extrae links sobre los elementos que le pasaremos (menú, footer o html), Función principal. Para cada url aportada, tiene como objetivo devolver un link

### Community 23 - "Candidate Services and UI"
Cohesion: 0.67
Nodes (4): backend/app/routers/candidates.py, backend/app/services/recommendations/courses_recommender.py, frontend/candidate/improve.py, frontend/candidate/jobs.py

## Knowledge Gaps
- **45 isolated node(s):** `UploadFile`, `entrypoint.sh script`, `Banner vertical branding MatchKey sidebar`, `Banner MatchKey login page`, `Illustration for candidate home page` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CandidateSkill` connect `Candidate Interview Management` to `Team and Company Profiles`, `System Initialization and Health`, `Candidate Job Matching Scores`, `Matching Engine Algorithms`, `Core Data Models`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `Job` connect `Candidate Interview Management` to `Team and Company Profiles`, `System Initialization and Health`, `Company Data and Culture`, `Candidate Job Matching Scores`, `Matching Engine Algorithms`, `Core Data Models`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `parse_candidate_cv()` connect `Candidate Interview Management` to `Resume Parsing and Extraction`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `Job` (e.g. with `Company` and `Job`) actually correct?**
  _`Job` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `User` (e.g. with `Path` and `Session`) actually correct?**
  _`User` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `Candidate` (e.g. with `Path` and `Session`) actually correct?**
  _`Candidate` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `CandidateSkill` (e.g. with `Path` and `Any`) actually correct?**
  _`CandidateSkill` has 45 INFERRED edges - model-reasoned connections that need verification._