# Matching Engine

## Purpose

Compute fit between a candidate and a job using skills, values and team fit.

## Source files

- [backend/app/routers/matching.py](../../backend/app/routers/matching.py)
- [backend/app/services/matching/matching_engine.py](../../backend/app/services/matching/matching_engine.py)
- [backend/app/services/matching/fit_scores.py](../../backend/app/services/matching/fit_scores.py)

## Formulae detected

The repository shows heuristic scoring rather than a single canonical ML model.

- Skills fit: based on coverage of must-have and nice-to-have skills.
- Values fit: based on overlap or proxy information from candidate and team data.
- Team fit: based on team profile descriptors and candidate text.
- Global fit: weighted or averaged combination of the three scores.

## Input / output

- Input: candidate skills, candidate profile, job skills and team profile.
- Output: score breakdown with `skills_fit`, `values_fit`, `team_fit` and `global_fit`.

## Current state

- Implemented, but simplified.
- The scoring logic is useful for the prototype and analytics pages, yet it should be treated as heuristic rather than authoritative.

## Limitations

- Some routes still return fixed values instead of fully computed scores.
- Matching uses text heuristics and normalized skill sets rather than a deeply semantic model.
- The design is extendable, but the current output is still a prototype.
