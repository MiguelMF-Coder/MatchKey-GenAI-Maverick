# Frontend Architecture

## Structure

The frontend lives under `frontend/` and is built with Streamlit.
The main entry point is `frontend/app.py`, which drives the public landing page, login and role-based portal navigation.
Shared helpers live in `frontend/utils.py`.

## Streamlit usage

- `app.py` defines the page configuration, theme and high-level routing.
- `utils.py` centralizes backend URL resolution and simple API helpers.
- Session state stores the authenticated user, role and current page.

## Detected pages and modules

### Candidate area

- `candidate/profile.py`
- `candidate/call_ai.py`
- `candidate/jobs.py`
- `candidate/improve.py`
- `candidate/dashboard.py`

### Company area

- `company/profile.py`
- `company/create_job.py`
- `company/analytics.py`
- `company/co_teaching.py`
- `company/dashboard.py`

## Candidate flow

1. The user logs in as candidate.
2. The landing and sidebar route them to candidate pages.
3. The profile page can upload a CV and call the backend parsing endpoint.
4. The jobs page fetches recommended jobs and score breakdowns.
5. The improvement page turns gaps into course recommendations.

## Company flow

1. The user logs in as company.
2. The profile page stores company data and cultural preferences.
3. The create-job page sends jobs and team profile data to the backend.
4. The analytics page asks for match distributions over company jobs.
5. The co-teaching page asks for complementary candidate pairs.

## Backend communication

The frontend uses `requests` and simple helper wrappers to call backend endpoints.
That integration is real and central to the app.
However, some pages assume contracts that are still simplified or only partially implemented.

## Real, dummy and pending parts

- Real: login, session state, role-based navigation, profile forms, job forms, recommendation views and analytics calls.
- Dummy / stub: the HR Copilot button in the UI is explicitly marked as upcoming, and some user-facing flows rely on backend placeholders.
- Pending: richer API contracts, stronger validation and any future UI screens not yet present in the repo.
