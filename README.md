# 🌟 README.md — Proyecto **MatchKey**

### *AI Mavericks – Accenture Challenge*

### Plataforma Inteligente de Matching de Empleo impulsada por IA y análisis avanzado

---

## 🧠 **¿Qué es MatchKey?**

**MatchKey** es un portal de empleo inteligente diseñado para resolver una de las mayores ineficiencias del mercado laboral:
**los procesos de selección lentos, impersonales y basados en filtros poco precisos**.

Nuestro sistema combina:

✅ Inteligencia Artificial
✅ Análisis semántico
✅ Matching multidimensional
✅ Multi-agentes MCP
✅ Experiencias personalizadas para empresas y candidatos
✅ RRHH humanizado gracias al HR Copilot

El resultado: **una plataforma que encuentra el encaje perfecto entre talento y vacantes**, considerando no solo habilidades técnicas, sino también valores, cultura, estilo de equipo y potencial de crecimiento.

---

# 🚀 **Características principales**

### 🎯 **Portal Candidato**

* Subida de CV con OCR (PDF/DOCX/Imagen)
* Extracción automática de skills técnicas
* Llamada IA simulada (HR Copilot)
* Recomendación de vacantes
* Skill gaps + cursos recomendados
* Resumen psicológico y valores personales

### 🏢 **Portal Empresa**

* Perfil corporativo + valores culturales
* Creación de vacantes (PDF → Must/Nice automáticamente)
* Analítica de talento
* Matching multidimensional:

  * Skills
  * Valores
  * Team-fit
* Módulo de **Co-Teaching** (parejas que se complementan)

---

# 🧱 **Arquitectura General**

**Frontend:** Streamlit
**Backend:** FastAPI
**Base de datos:** PostgreSQL
**Orquestación:** Docker
**Sistema de IA:** MCP Multi-agente (Document Parser, Skills Extractor, HR Copilot, Matching Engine, Co-Teaching…)

---

# 📂 **Estructura del repositorio**

```
matchkey/
│
├── docker-compose.yml
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── routers/
│       ├── services/
│       ├── models/
│       └── db/
│
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── utils.py
│   ├── candidate/
│   └── company/
│
└── docs/
```

---

# 🤖 **Sistema MCP — Multi-Agente**

### 1. **Document Parser (Pablo M)**

Lee PDFs/DOCX/Imágenes → limpia texto → devuelve:

```json
{ "raw_text": "...", "clean_text": "...", "metadata": {...} }
```

### 2. **Skills Extractor (Pablo M)**

Detecta skills exactas, por TF-IDF y embeddings → clasifica Must/Nice.

### 3. **HR Copilot (Asier)**

Extrae motivaciones, valores, soft skills, preferencia de equipo y resumen psicológico.

### 4. **Matching Engine (Miguel)**

```
global_score = 0.5*skills + 0.3*values + 0.2*team_fit
```

### 5. **Co-Teaching Engine (Miguel)**

Detecta parejas de candidatos que juntos cubren mejor una vacante.

### 6. **Scraping & Datasets (Pablo)**

Valores culturales y cursos recomendados.

---

# 🎨 **Frontend – Streamlit**

Separado por roles con `session_state["role"]`:

### Candidato

* Dashboard
* Mi perfil (subida CV)
* Llamada IA
* Vacantes recomendadas
* Mejora (gaps + cursos)

### Empresa

* Dashboard
* Perfil + valores
* Crear vacante (PDF → Must/Nice)
* Analítica de talento
* Co-Teaching

Tema visual: **Accenture Purple (#A100FF)**

---

# 📡 **Backend – FastAPI**

Rutas principales:

### Candidatos

```
/candidates/create
/candidates/{id}/profile
/candidates/{id}/recommended_jobs
/candidates/{id}/job/{job}/gaps
```

### Empresas

```
/companies/create
/companies/{id}/profile
```

### Vacantes

```
/jobs/create
/jobs/{id}/extract_skills
/jobs/{id}/match_candidates
/jobs/{id}/co_teaching
```

### HR Copilot

```
/copilot/process_call
```

---

# 🗄️ **Base de Datos – Esquema mínimo**

Tablas principales:

* users
* candidates
* candidate_skills
* candidate_interviews
* companies
* jobs
* job_skills
* team_profiles
* personality_quiz_results

---

# 🐳 **Docker – Infraestructura completa**

Tres servicios:

```
frontend  → localhost:8501  
backend   → localhost:8000  
db        → PostgreSQL
```

---

# 👥 **Equipo y roles**

| Miembro     | Rol                                                   | Responsabilidad                                |
| ----------- | ----------------------------------------------------- | ---------------------------------------------- |
| **Miguel**  | Arquitectura · Backend · Frontend · Matching · Docker | Base técnica del sistema                       |
| **Pablo**   | Scraping                                              | Valores, cursos, datasets y adapters           |
| **Pablo M** | OCR + Skills                                          | Document Parser + Skills Extractor + Must/Nice |
| **Asier**   | HR Copilot                                            | Análisis semántico y entrevista IA             |
| **Jack**    | Presentación · Ética · Viabilidad                     | Defensa del proyecto                           |

---

# 🟣 **Instrucciones para desarrolladores**

Siempre seguir la estructura y nombres definidos.
Los módulos MCP, rutas y archivos **no deben renombrarse**.
Cada feature → su rama:

```
feature/miguel-*
feature/pablo-scraping
feature/pablom-ocr-skills
feature/asier-hrcopilot
feature/jack-docs
```

---

# 🏁 **Estado del Proyecto**

✔ Estructura base creada
✔ Documentación completa
✔ Módulos MCP definidos
✔ Frontend y backend conectados
✔ Rutas dummy listas
⏳ Integración completa de agentes
⏳ Ajustes finales y demo

---

# ✨ **Visión**

MatchKey no es solo un portal de empleo.
Es **una nueva forma de conectar personas con oportunidades**, donde la IA **no deshumaniza**, sino que **entiende, recomienda y acompaña**.

