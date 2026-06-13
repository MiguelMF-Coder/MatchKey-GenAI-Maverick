# Co-Teaching

## Purpose

Find pairs of candidates that together cover a job better than each one alone.

## Source files

- [backend/app/routers/jobs.py](../../backend/app/routers/jobs.py)
- [backend/app/models/jobs.py](../../backend/app/models/jobs.py)

## Logic detected

- The backend exposes a co-teaching route under jobs.
- The current implementation returns a dummy pair when there are at least two candidates.
- The response includes pair coverage, risk, global score and complementarities.

## Input / output

- Input: job ID and current candidate set.
- Output: list of pairs with candidate A, candidate B and pair metrics.

## Current state

- Dummy/stub.
- The data model exists and the endpoint shape is in place, but the recommendation engine is not yet real.

## Relationship with company analytics

- Co-Teaching is part of the company-facing experience.
- It is conceptually aligned with the analytics and job-management views.
- It should eventually reuse richer matching and profile data.
