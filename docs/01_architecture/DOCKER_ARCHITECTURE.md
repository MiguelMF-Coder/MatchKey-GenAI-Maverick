# Docker Architecture

## Services detected

| service | image / build | ports | purpose |
| --- | --- | --- | --- |
| `db` | `postgres:16` | `5432:5432` | PostgreSQL database |
| `backend` | build from `./backend` | `8000:8000` | FastAPI API |
| `frontend` | build from `./frontend` | `8501:8501` | Streamlit app |
| `pgadmin` | `dpage/pgadmin4` | `5050:80` | Optional database UI |

## Environment variables detected

- Database: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- Backend: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- Frontend: `BACKEND_URL`.
- pgAdmin: `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`.

## Dockerfiles detected

- `backend/Dockerfile` installs system libraries, Python requirements, spaCy model and backend app code.
- `frontend/Dockerfile` installs requirements and launches Streamlit.

## Reproducibility value

Docker makes the project easier to run with consistent dependencies, especially because the backend needs system packages for OCR, PDF handling and PostgreSQL drivers.
The containers also provide a stable way to reproduce the backend/frontend split used in the repo.

## What still needs confirmation

- Whether all runtime environment variables are documented outside docker-compose.
- Whether the backend entrypoint script matches the current deployment expectations everywhere.
- Whether additional services are needed for future phases, such as a real queue or LLM gateway.
