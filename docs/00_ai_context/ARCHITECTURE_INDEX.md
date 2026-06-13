# Architecture Index

This file is the entry point for understanding the MatchKey architecture.
Use it to locate the current documentation, understand the recommended reading order, and see what is still pending.

## Recommended reading order for AI

1. [AGENTS.md](../../AGENTS.md)
2. [docs/00_ai_context/AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md)
3. [docs/00_ai_context/MATCHKEY_CONTEXT.md](MATCHKEY_CONTEXT.md)
4. [docs/00_ai_context/GRAPHIFY_WORKFLOW.md](GRAPHIFY_WORKFLOW.md)
5. [graphify-out/graph.json](../../graphify-out/graph.json)
6. [README.md](../../README.md)

## Recommended reading order for humans

1. [README.md](../../README.md)
2. [docs/00_ai_context/MATCHKEY_CONTEXT.md](MATCHKEY_CONTEXT.md)
3. [docs/README_DOCS.md](../README_DOCS.md)
4. future architecture documentation
5. future module documentation

## Current documentation map

| file | purpose | state |
| --- | --- | --- |
| `README.md` | Main project overview and contributor guidance | external |
| `AGENTS.md` | Short AI entry instruction for the repo | created |
| `docs/README_DOCS.md` | Documentation hub and section map | created |
| `docs/00_ai_context/MATCHKEY_CONTEXT.md` | Base project context for humans and IAs | created |
| `docs/00_ai_context/GRAPHIFY_WORKFLOW.md` | Graphify workflow, artifacts, and usage rules | created |
| `docs/00_ai_context/AGENT_INSTRUCTIONS.md` | Working rules for any AI agent in this repo | created |
| `graphify-out/graph.json` | Current structural graph of the repository | generated |
| `graphify-out/manifest.json` | Graphify provenance metadata | generated |
| `graphify-out/GRAPH_REPORT.md` | Human-readable graph summary | generated |
| `graphify-out/graph.html` | Interactive graph visualization | generated |

## Recommended pending documentation

These files are planned but must not be created in this phase.

| file | purpose |
| --- | --- |
| `docs/01_architecture/SYSTEM_OVERVIEW.md` | High-level system architecture |
| `docs/01_architecture/BACKEND_ARCHITECTURE.md` | Backend structure and responsibilities |
| `docs/01_architecture/FRONTEND_ARCHITECTURE.md` | Streamlit structure and navigation |
| `docs/01_architecture/MCP_AGENTS.md` | Agent and MCP-oriented workflow overview |
| `docs/01_architecture/DATABASE_MODEL.md` | Data model and persistence overview |
| `docs/01_architecture/DOCKER_ARCHITECTURE.md` | Container and orchestration overview |
| `docs/02_api/API_ROUTES.md` | Route inventory and route purpose map |
| `docs/02_api/API_CONTRACTS.md` | Request and response contracts |
| `docs/03_modules/document_parser.md` | Document parsing module documentation |
| `docs/03_modules/skills_extractor.md` | Skills extraction module documentation |
| `docs/03_modules/hr_copilot.md` | HR copilot module documentation |
| `docs/03_modules/matching_engine.md` | Matching engine module documentation |
| `docs/03_modules/co_teaching.md` | Co-teaching module documentation |
| `docs/03_modules/scraping_values_courses.md` | Scraping and datasets documentation |
| `docs/04_user_flows/candidate_flow.md` | Candidate flow documentation |
| `docs/04_user_flows/company_flow.md` | Company flow documentation |
| `docs/05_decisions/ADR-001-stack.md` | Initial architecture decision record |

## Pending note

The files listed above are only recommendations for later phases.
They must remain pending until their phase is explicitly started.
