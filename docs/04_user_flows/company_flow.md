# Company Flow

## End-to-end flow

1. The company logs in from the public landing page.
2. The frontend stores the authenticated role and company ID in session state.
3. The company completes its profile and culture fields.
4. The company creates a job with team context.
5. The backend stores the job and generates dummy or simplified skill data where needed.
6. The company inspects candidate matching results and analytics.
7. The company explores Co-Teaching suggestions for a job.

## Implemented parts

- Company login and profile CRUD.
- Job creation and update.
- Jobs with applications list.
- Analytics view that queries matching scores.

## Dummy / stub parts

- Job skill extraction is currently heuristic and sometimes seeded with fixed values.
- Candidate matching suggestions and Co-Teaching are simplified or dummy in the current implementation.

## Pending parts

- Richer job parsing from uploaded descriptions.
- Real matching and co-teaching ranking logic.
- Deeper analytics beyond the current heuristic outputs.
