# ADR-002: Modular Agents

## Decision

Organize the project around modular tool-like components for OCR, skills extraction, HR copilot, matching, scraping and recommendation logic.

## Context

MatchKey needs several specialized flows that do not belong in a single monolithic function.
The repository already reflects this separation in its services and router structure.

## Why this approach

- It keeps concerns isolated.
- It lets future agents and humans reason about each capability separately.
- It makes it easier to replace stubs with stronger implementations later.
- It matches the repo's MCP-oriented language and the Graphify navigation model.

## Benefits

- Better maintainability.
- Easier documentation.
- Easier testing and gradual replacement of placeholder logic.
- Better fit with AI-assisted development workflows.

## Risks

- More moving parts.
- Some contract drift between frontend and backend if modules evolve independently.
- Stubbed modules can look more complete than they are if not clearly labeled.

## Consequences

- Documentation must distinguish real, partial, stub and pending logic.
- The graph and the docs become important navigation tools, not just extras.
