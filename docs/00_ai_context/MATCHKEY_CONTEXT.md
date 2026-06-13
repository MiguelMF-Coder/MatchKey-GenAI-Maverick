# MatchKey Context

MatchKey is an AI-assisted job matching platform.
It combines candidate and company workflows in one repository.
The goal is to compare skills, values, team fit, and job requirements.
The current codebase shows a modular backend, a Streamlit frontend, and shared AI-oriented services.
The project is organized to support OCR, skill extraction, HR copilot logic, matching, scraping, and recommendation flows.
Some parts are implemented, while others are still stubbed or marked as future work.
This document is the initial context layer for humans and IAs.

## Detected stack

- FastAPI for the backend API.
- Streamlit for the frontend portal.
- PostgreSQL for persistence.
- Docker and docker-compose for local orchestration.
- Modular service layout with MCP-oriented language in the repo and skill/tool separation in the backend.

## Main product split

- Candidate portal: profile, CV/OCR flow, HR copilot call, recommended jobs, gaps, and course suggestions.
- Company portal: company profile, job creation, analytics, matching views, and co-teaching flows.

## General repo structure

- `backend/`: FastAPI app, models, routers, services, database helpers, and tests.
- `frontend/`: Streamlit app with candidate and company pages.
- `app/`: shared or alternative top-level app code used by the project.
- `docs/`: planning and support documentation.
- `graphify-out/`: generated graph artifacts and caches.
- `kb/`: knowledge-base related material.

## Main folders detected

- `backend/app/routers/`
- `backend/app/services/`
- `backend/app/models/`
- `backend/app/db/`
- `frontend/candidate/`
- `frontend/company/`
- `backend/app/services/ocr/`
- `backend/app/services/matching/`
- `backend/app/services/hr_copilot/`
- `backend/app/services/scraping/`

## Main modules and services detected

- Backend entry point and API setup in `backend/app/main.py`.
- Candidate, company, jobs, copilot, matching, and auth routers.
- OCR/document parsing service.
- Skills extraction service.
- HR copilot tool.
- Matching engine and score helpers.
- Course recommendation service.
- Scraping services for jobs, companies, courses, and universities.
- Streamlit portal entry point and role-based pages.

## Current project state

- Implemented: repository structure, FastAPI routers, Streamlit role split, matching logic, database models, scraping helpers, and graphify-generated structural context.
- Stub or dummy: HR copilot tool output, skills extraction logic, and some explanatory text paths that still say they are placeholders.
- Pending: deeper LLM-backed analysis, richer semantic extraction, and any future features not yet implemented in code.
