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
| `docs/00_ai_context/ARCHITECTURE_INDEX.md` | Architecture reading order and documentation map | created |
| `docs/01_architecture/SYSTEM_OVERVIEW.md` | High-level system architecture | created |
| `docs/01_architecture/BACKEND_ARCHITECTURE.md` | Backend structure and service map | created |
| `docs/01_architecture/FRONTEND_ARCHITECTURE.md` | Streamlit structure and user portals | created |
| `docs/01_architecture/MCP_AGENTS.md` | MCP/tool-oriented service map | created |
| `docs/01_architecture/DATABASE_MODEL.md` | Database entities and relationships | created |
| `docs/01_architecture/DOCKER_ARCHITECTURE.md` | Docker and runtime orchestration | created |
| `docs/02_api/API_ROUTES.md` | FastAPI route inventory | created |
| `docs/02_api/API_CONTRACTS.md` | Detected request/response contracts | created |
| `docs/03_modules/document_parser.md` | Document parser module documentation | created |
| `docs/03_modules/skills_extractor.md` | Skills extractor module documentation | created |
| `docs/03_modules/hr_copilot.md` | HR copilot module documentation | created |
| `docs/03_modules/matching_engine.md` | Matching engine module documentation | created |
| `docs/03_modules/co_teaching.md` | Co-teaching module documentation | created |
| `docs/03_modules/scraping_values_courses.md` | Scraping and datasets documentation | created |
| `docs/04_user_flows/candidate_flow.md` | Candidate journey documentation | created |
| `docs/04_user_flows/company_flow.md` | Company journey documentation | created |
| `docs/05_decisions/ADR-001-stack.md` | Stack decision record | created |
| `docs/05_decisions/ADR-002-modular-agents.md` | Modular agents decision record | created |
| `docs/05_decisions/ADR-003-graphify-ai-context.md` | Graphify and AI-context decision record | created |
| `graphify-out/graph.json` | Current structural graph of the repository | generated |
| `graphify-out/manifest.json` | Graphify provenance metadata | generated |
| `graphify-out/GRAPH_REPORT.md` | Human-readable graph summary | generated |
| `graphify-out/graph.html` | Interactive graph visualization | generated |

## Pending note

The roadmap section is intentionally light here because the files in this phase were created now.
Any deeper documentation should be added only in later phases and should stay clearly marked as pending until implemented.
