# MCP Agents

## Concept in MatchKey

MatchKey uses MCP-like language to describe a modular AI toolchain.
In practice, the repo contains services and scripts that behave like tools or agents, even if not all of them are wired to a live MCP runtime yet.
This architecture lets the project separate document parsing, skill extraction, HR analysis, matching, co-teaching and scraping into focused pieces.

## Detected tools and agents

| module | role | input | output | state |
| --- | --- | --- | --- | --- |
| `ocr/document_parser.py` | CV reader and parser | uploaded CV file | structured CV dict | implemented |
| `skills/skills_extractor.py` | Skill extraction baseline | raw text | must/nice/all skills dict | partially implemented / dummy |
| `hr_copilot/hr_copilot_tool.py` | HR interview summarizer | answers list | profile JSON | dummy/stub |
| `matching/matching_engine.py` | Fit scoring engine | candidate + job | score dict | implemented with heuristics |
| `jobs.py` co-teaching endpoint | co-teaching suggestion stub | job and candidates | pair list | stub |
| `courses_recommender.py` | course suggestion helper | missing skills | course list | implemented |
| scraping scripts | offline data generation tools | websites / datasets | JSON / CSV datasets | implemented as scripts |
| `mcp_client.py` | future MCP transport wrapper | tool name + payload | echo / placeholder dict | stub |

## Expected I/O patterns

- Document parser: file in, structured text and metadata out.
- Skills extractor: parsed text in, skill buckets out.
- HR copilot: question/answer text in, motivations/values/summary out.
- Matching engine: candidate/job in, score breakdown out.
- Co-teaching: job and candidate pool in, pair recommendations out.
- Scraping tools: source websites in, curated datasets out.

## How they should integrate with the backend

- The backend routes should orchestrate the tools and persist results.
- The frontend should remain thin and only call the backend.
- Long-running or offline scraping should stay outside the request path.

## Real state

- Real: parser, course recommender, score engine and data-model relationships.
- Partially implemented: skills extraction, job extraction and matching helpers in some routes.
- Dummy / stub: HR Copilot and MCP transport client.
- Pending: actual MCP runtime integration if the project decides to activate it later.
