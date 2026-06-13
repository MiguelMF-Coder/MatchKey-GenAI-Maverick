# System Overview

## What MatchKey is

MatchKey is an AI-assisted job matching platform focused on two sides of the market:
candidate and company.
It aims to match people and opportunities not only by technical skills, but also by values, culture, team fit and career context.
The repository shows a modular Python stack with a FastAPI backend, a Streamlit frontend, PostgreSQL persistence and Docker-based runtime orchestration.
Graphify is used as a structural documentation layer so future humans and IAs can navigate the repo before reading raw files.

## Vision of the system

- Reduce manual filtering in hiring workflows.
- Let candidates upload a CV, enrich their profile and discover better matches.
- Let companies define culture, create jobs and inspect candidates and team fit.
- Keep the architecture modular so each part can evolve independently.

## Main portals

### Candidate portal

- Profile management.
- CV upload and OCR / parsing flow.
- HR copilot questionnaire.
- Recommended jobs.
- Gap analysis and course suggestions.

### Company portal

- Company profile and culture definition.
- Job creation.
- Talent analytics.
- Candidate matching.
- Co-Teaching views.

## Stack detected

- Backend: FastAPI.
- Frontend: Streamlit.
- Database: PostgreSQL.
- Runtime: Docker and docker-compose.
- Supporting services: OCR, skills extraction, matching, recommendations, scraping, notifications and Graphify-generated context.

## Modular architecture

The repo separates the project into backend routers, backend services, SQLAlchemy models, Streamlit pages and scraping/data scripts.
The code is not a pure microservice architecture, but it is clearly divided into modules that behave like bounded domains.
Several parts are implemented with real data flow, while others are still stubs or placeholders.

## Frontend / backend / database relation

- Streamlit calls the backend with HTTP requests.
- The backend reads and writes SQLAlchemy models against PostgreSQL.
- Some backend routes seed or reuse data on startup.
- The frontend keeps minimal session state and delegates the domain logic to the backend.

## Role of Graphify

Graphify provides the current structural graph of the repository.
It helps future agents understand dependencies, hubs and module relationships before browsing files manually.
The graph is a navigation aid, not a replacement for source code or tests.

## Current state

- Implemented: main portals, router structure, SQLAlchemy models, startup seeds, Graphify context, and several real backend/frontend flows.
- Partially implemented: matching and analytics use simplified heuristics in some paths.
- Dummy / stub: HR copilot output, some job-matching endpoints, the legacy CV parse endpoint, and some extraction paths that still contain placeholder values.
- Pending: more detailed semantic AI behavior, richer matching logic, and deeper documentation for each module.

## Known limitations

- The architecture mixes real logic with placeholder values in a few endpoints.
- Some frontend screens assume richer backend contracts than are currently guaranteed.
- The copilot endpoint exists in code but is not mounted in the main FastAPI app.
- Some datasets and scraping flows are script-driven rather than exposed as runtime services.
