# ADR-001: Stack Choice

## Decision

Use FastAPI for the backend, Streamlit for the frontend, PostgreSQL for persistence and Docker for runtime orchestration.

## Context

The repository shows a Python-first product with data processing, OCR, scraping, recommendation and matching logic.
That makes Python a natural fit for both backend orchestration and analytical services.

## Why this stack

- FastAPI gives a lightweight and typed API layer.
- Streamlit gives a fast way to build role-based internal UIs.
- PostgreSQL provides a solid relational base for candidate, company, job and matching data.
- Docker reduces environment drift and makes the OCR / PDF / PostgreSQL dependencies reproducible.

## Alternatives considered

The repository does not explicitly document alternatives, so they are not claimed here.
The current choice is best understood as an implementation-first decision aligned with the project scope.

## Consequences

- Faster prototype delivery.
- Strong Python compatibility across the stack.
- Clear separation between UI and API.
- Need to manage some contract alignment carefully because parts of the system are still evolving.
