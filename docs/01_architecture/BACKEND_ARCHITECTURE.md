# Backend Architecture

## Structure

The backend lives under `backend/app/` and is organized into:

- `main.py`: FastAPI application bootstrap.
- `routers/`: HTTP endpoints grouped by domain.
- `services/`: OCR, skills, HR copilot, matching, scraping, recommendations and notifications.
- `models/`: SQLAlchemy entities.
- `db/`: database session setup, initialization and seed scripts.

## FastAPI routers detected

| router | purpose | state |
| --- | --- | --- |
| `auth` | Login and user-role bootstrap | implemented |
| `candidates` | Candidate profile, CV parsing, recommendations and gaps | implemented with some stub paths |
| `companies` | Company profile and company jobs overview | implemented |
| `jobs` | Job creation, applications, matching and co-teaching | partially implemented |
| `matching` | Match score calculation endpoint | implemented with simplified heuristics |
| `copilot` | HR Copilot call processing | present in code, not mounted in `main.py` |

## Services detected

| service | purpose | state |
| --- | --- | --- |
| `ocr/document_parser.py` | Parse CV files into structured text/data | implemented |
| `skills/skills_extractor.py` | Extract skills from text using a dictionary-based baseline | partially implemented / dummy logic |
| `hr_copilot/hr_copilot_tool.py` | Produce interview-like profile data | dummy/stub |
| `matching/matching_engine.py` | Compute skills, values, team and global fit | implemented with heuristic scoring |
| `matching/fit_scores.py` | Additional score helpers | implemented |
| `recommendations/courses_recommender.py` | Recommend courses for skill gaps | implemented |
| `notifications/email_service.py` | Send or simulate preselection emails | implemented with dev fallback |
| `scraping/*` | Build datasets for jobs, companies, universities and courses | implemented as scripts / offline preprocessing |
| `mcp_client.py` | Stub client for future MCP tool calls | stub |

## Models and base data

Detected entities include users, candidates, companies, company culture, jobs, team profiles, team members, candidate skills, job skills, candidate interviews, applications, job recommendations and co-teaching pairs.
The models are real SQLAlchemy classes, but there is no obvious migration system in this snapshot.

## Communication between routes and services

- Candidate routes call OCR parsing and course recommendation helpers.
- Job routes create jobs, seed skills, compute candidate lists and build co-teaching results.
- Matching routes compute fit scores from candidate and job models.
- Auth routes bootstrap user/candidate/company records.
- Company routes expose profile and job aggregates.

## Real, stub and pending parts

- Real: auth, profile CRUD, CV parsing, matching score endpoint, job CRUD, company profile CRUD, seeders and most model relationships.
- Stub / dummy: HR Copilot results, some score generation in job recommendations, legacy parse endpoint and job matching candidate lists.
- Pending: richer semantic extraction, full co-teaching logic and stronger contract alignment with the Streamlit UI.

## Integration risks

- Some frontend calls expect richer payloads than the backend currently guarantees.
- The copilot route is defined but not mounted in `main.py`.
- Several heuristics are good enough for a prototype but should be treated as provisional.
- Startup seeds may create data automatically, which is useful for demos but should be documented carefully in later phases.
