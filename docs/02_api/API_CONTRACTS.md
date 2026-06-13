# API Contracts

## Auth

### POST /auth/login

Request:

- `email` string
- `password` string
- `role` one of `candidate` or `company`

Response:

- `user_id`
- `email`
- `role`
- `candidate_id` or `company_id`

## Candidates

### POST /candidates/create

Request:

- `email`
- `name` optional

Response:

- Candidate profile payload with profile fields, skills count and interview flag.

### GET /candidates/{candidate_id}/profile

Response:

- Candidate profile payload.

### PUT /candidates/{candidate_id}/profile

Request:

- Editable profile fields such as name, headline, location, summary, years_experience, contact_email and contact_phone.

Response:

- Updated candidate profile payload.

### POST /candidates/{candidate_id}/parse_cv

Request:

- multipart file upload named `file`.

Response:

```json
{
  "status": "success",
  "candidate_id": 1,
  "updated_candidate": {},
  "skills_detected": [],
  "parsed_cv": {}
}
```

### GET /candidates/{candidate_id}/recommended_jobs

Response:

- `{ "jobs": [...] }` where each job includes a `scores` object.

### GET /candidates/{candidate_id}/job/{job_id}/gaps

Response shape detected:

- `scores`
- `skills` with strong / medium / missing buckets
- `recommendations` with courses and actions

Some values are currently simplified or placeholder-based.

### GET /candidates/{candidate_id}/job/{job_id}/recommended_courses

Response:

- `candidate_id`
- `job_id`
- `missing_skills`
- `courses`

### GET /candidates/courses

Response:

- list of course dictionaries from the static dataset.

## Companies

### POST /companies/create

Request:

- `email`
- `name` optional

Response:

- company profile payload including values, culture info and jobs list.

### GET /companies/{company_id}/profile

Response:

- company profile payload with jobs list.

### PUT /companies/{company_id}/profile

Request:

- company metadata and culture fields.

Response:

- updated company profile payload.

### GET /companies/{company_id}/jobs_with_applications

Response:

- `company_id`
- `company_name`
- `jobs` list with application counts.

## Jobs

### POST /jobs/create

Request:

- job metadata, optional `jd_text`, optional team profile, optional `auto_extract_skills`.

Response:

- job detail payload with `must_have`, `nice_to_have`, `all_skills` and `team_profile`.

### GET /jobs/{job_id}/extract_skills

Response:

- same job detail payload after re-extracting skills.

### GET /jobs/{job_id}/match_candidates

Response:

- `{ "job_id": ..., "candidates": [...] }`
- candidate items include `candidate_id`, `name`, `email`, `scores`, and optional `raw_match_data`.

### GET /jobs/{job_id}/co_teaching

Response:

- `{ "job_id": ..., "pairs": [...] }`
- pair items include candidate A/B, coverage, risk, global score and complementarities.

### POST /jobs/{job_id}/apply

Request:

- `candidate_id`

Response:

- status, message and `application_id`.

### GET /jobs/{job_id}/applications

Response:

- job title and applications list.

### POST /jobs/{job_id}/applications/{application_id}/select

Response:

- selection confirmation, application_id, candidate_id and job_id.

### PUT /jobs/{job_id}

Response:

- updated job detail payload.

### DELETE /jobs/{job_id}

Response:

- `{ "status": "ok", "message": ..., "job_id": ... }`

## Matching

### GET /matching/candidates/{candidate_id}/job/{job_id}/scores

Response:

- `skills_fit`
- `values_fit`
- `team_fit`
- `global_fit`

## Copilot

### POST /copilot/process_call

Current code intent:

- `candidate_id`
- answers payload

Current caveat:

- The route is not mounted in `main.py`.
- The frontend currently sends a list of question/answer objects, while the backend signature is still loose and expects `answers: list[str]`.
- Treat this contract as pending until the route is explicitly aligned and exposed.
