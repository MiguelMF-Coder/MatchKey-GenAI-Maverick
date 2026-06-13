# MatchKey Documentation

This directory organizes the documentation for MatchKey in progressive layers.
The goal is to keep a reliable base for humans and IAs, then expand into architecture, API, module, flow, and decision documentation.
This phase adds the first technical layers beyond the AI context base.

## Sections

### 00_ai_context

Initial context for humans and IAs.
It explains what MatchKey is, how Graphify is used, and which instructions should be read first.

Files:
- [MATCHKEY_CONTEXT.md](00_ai_context/MATCHKEY_CONTEXT.md)
- [GRAPHIFY_WORKFLOW.md](00_ai_context/GRAPHIFY_WORKFLOW.md)
- [AGENT_INSTRUCTIONS.md](00_ai_context/AGENT_INSTRUCTIONS.md)
- [ARCHITECTURE_INDEX.md](00_ai_context/ARCHITECTURE_INDEX.md)

### 01_architecture

Planned architecture-level documentation.
It will describe the system, backend, frontend, MCP-style services, database model, and Docker setup.

Files:
- [SYSTEM_OVERVIEW.md](01_architecture/SYSTEM_OVERVIEW.md)
- [BACKEND_ARCHITECTURE.md](01_architecture/BACKEND_ARCHITECTURE.md)
- [FRONTEND_ARCHITECTURE.md](01_architecture/FRONTEND_ARCHITECTURE.md)
- [MCP_AGENTS.md](01_architecture/MCP_AGENTS.md)
- [DATABASE_MODEL.md](01_architecture/DATABASE_MODEL.md)
- [DOCKER_ARCHITECTURE.md](01_architecture/DOCKER_ARCHITECTURE.md)

### 02_api

Planned API documentation.
It will list routes, request and response contracts, and expected backend behavior.

Files:
- [API_ROUTES.md](02_api/API_ROUTES.md)
- [API_CONTRACTS.md](02_api/API_CONTRACTS.md)

### 03_modules

Planned module-level documentation.
It will describe individual services such as document parsing, skills extraction, HR copilot, matching, co-teaching, and scraping.

Files:
- [document_parser.md](03_modules/document_parser.md)
- [skills_extractor.md](03_modules/skills_extractor.md)
- [hr_copilot.md](03_modules/hr_copilot.md)
- [matching_engine.md](03_modules/matching_engine.md)
- [co_teaching.md](03_modules/co_teaching.md)
- [scraping_values_courses.md](03_modules/scraping_values_courses.md)

### 04_user_flows

Planned user-flow documentation.
It will explain the candidate and company journeys at a higher level.

Files:
- [candidate_flow.md](04_user_flows/candidate_flow.md)
- [company_flow.md](04_user_flows/company_flow.md)

### 05_decisions

Planned decision records.
It will capture important architecture choices and the reasons behind them.

Files:
- [ADR-001-stack.md](05_decisions/ADR-001-stack.md)
- [ADR-002-modular-agents.md](05_decisions/ADR-002-modular-agents.md)
- [ADR-003-graphify-ai-context.md](05_decisions/ADR-003-graphify-ai-context.md)

## Current status

For now, the AI context base and the first technical documentation layer are available.
The documentation will continue to grow progressively in later phases.
