# Candidate Flow

## End-to-end flow

1. The candidate logs in from the public landing page.
2. The frontend stores the authenticated role and candidate ID in session state.
3. The candidate opens the profile page and uploads a CV.
4. The backend parses the CV, updates candidate data and stores detected skills.
5. The candidate reviews recommended jobs and score breakdowns.
6. The candidate checks gap analysis for a specific job.
7. The candidate sees suggested courses for missing skills.

## Implemented parts

- Login flow.
- Candidate profile CRUD.
- CV parsing endpoint.
- Recommended jobs view.
- Gap analysis and recommended courses.

## Dummy / stub parts

- The HR Copilot page has a future-facing voice/chat button that is explicitly marked as upcoming.
- The HR Copilot backend output is still dummy.

## Pending parts

- A fully live HR Copilot experience.
- Stronger semantic enrichment and richer match explanations.
- Further validation of the frontend/backend contract for all fields displayed in the profile page.
