# API Routes

## Auth

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| POST | `/auth/login` | Create or validate a user and return role-specific IDs | `backend/app/routers/auth.py` | implemented |

## Candidates

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| POST | `/candidates/create` | Create or reuse a candidate profile | `backend/app/routers/candidates.py` | implemented |
| GET | `/candidates/{candidate_id}/profile` | Read candidate profile | `backend/app/routers/candidates.py` | implemented |
| PUT | `/candidates/{candidate_id}/profile` | Update candidate profile | `backend/app/routers/candidates.py` | implemented |
| POST | `/candidates/{candidate_id}/profile` | Legacy CV upload and parse endpoint | `backend/app/routers/candidates.py` | dummy/stub |
| GET | `/candidates/{candidate_id}/recommended_jobs` | Return recommended jobs with scores | `backend/app/routers/candidates.py` | implemented |
| GET | `/candidates/{candidate_id}/job/{job_id}/gaps` | Return gap analysis for a job | `backend/app/routers/candidates.py` | implemented with simplified values |
| GET | `/candidates/courses` | Return course catalog | `backend/app/routers/candidates.py` | implemented |
| GET | `/candidates/{candidate_id}/job/{job_id}/recommended_courses` | Return courses for job gaps | `backend/app/routers/candidates.py` | implemented |
| POST | `/candidates/{candidate_id}/parse_cv` | Parse uploaded CV and update candidate data | `backend/app/routers/candidates.py` | implemented |

## Companies

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| POST | `/companies/create` | Create or reuse a company profile | `backend/app/routers/companies.py` | implemented |
| GET | `/companies/{company_id}/profile` | Read company profile and jobs | `backend/app/routers/companies.py` | implemented |
| PUT | `/companies/{company_id}/profile` | Update company profile and culture | `backend/app/routers/companies.py` | implemented |
| GET | `/companies/{company_id}/jobs_with_applications` | List jobs with application counts | `backend/app/routers/companies.py` | implemented |

## Jobs

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| POST | `/jobs/create` | Create a job, team profile and dummy skills | `backend/app/routers/jobs.py` | partially implemented |
| GET | `/jobs/{job_id}/extract_skills` | Re-extract skills from job text | `backend/app/routers/jobs.py` | partially implemented |
| GET | `/jobs/{job_id}/match_candidates` | Return candidate matches for a job | `backend/app/routers/jobs.py` | dummy/stub |
| GET | `/jobs/{job_id}/co_teaching` | Return co-teaching pairs | `backend/app/routers/jobs.py` | dummy/stub |
| POST | `/jobs/{job_id}/apply` | Create a job application | `backend/app/routers/jobs.py` | implemented |
| GET | `/jobs/{job_id}/applications` | List applications for a job | `backend/app/routers/jobs.py` | implemented |
| POST | `/jobs/{job_id}/applications/{application_id}/select` | Select a candidate and trigger email | `backend/app/routers/jobs.py` | implemented with email fallback |
| PUT | `/jobs/{job_id}` | Update a job | `backend/app/routers/jobs.py` | implemented |
| DELETE | `/jobs/{job_id}` | Delete job and related data | `backend/app/routers/jobs.py` | implemented |

## Matching

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| GET | `/matching/candidates/{candidate_id}/job/{job_id}/scores` | Compute score breakdown | `backend/app/routers/matching.py` | implemented |

## Copilot

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| POST | `/copilot/process_call` | Process HR Copilot answers | `backend/app/routers/copilot.py` | present in code, not mounted in `main.py` |

## Health

| method | route | purpose | module | state |
| --- | --- | --- | --- | --- |
| GET | `/health` | Basic API health check | `backend/app/main.py` | implemented |

## Notes

- No invented routes are listed here.
- Some routes use simplified or placeholder outputs and are marked accordingly.
- The copilot route exists as code but is currently not exposed by the FastAPI app bootstrap.
