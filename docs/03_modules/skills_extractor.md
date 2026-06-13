# Skills Extractor

## Purpose

Extract technical skills from text and split them into Must Have and Nice to Have buckets.

## Source file

- [backend/app/services/skills/skills_extractor.py](../../backend/app/services/skills/skills_extractor.py)

## Main behavior

- Loads a skills dictionary from `skills_dictionary.json` when available.
- Normalizes text.
- Detects known skills through dictionary matching.
- Classifies the first two hits as `must_have` and the rest as `nice_to_have`.

## Input / output

- Input: raw job or CV text.
- Output: dict with `must_have`, `nice_to_have` and `all_skills`.

## Must Have / Nice to Have

- The split exists in the code.
- The current implementation is baseline and order-based rather than semantic.
- More advanced TF-IDF or embeddings logic is still pending.

## Current state

- Partially implemented.
- The module is functional as a baseline, but the docstring and comments make clear that it is still a placeholder for richer extraction.

## Integration with matching

- Job skills and candidate skills feed the matching score logic.
- The backend currently uses simplified extraction in job routes while keeping this service as the intended expansion point.
