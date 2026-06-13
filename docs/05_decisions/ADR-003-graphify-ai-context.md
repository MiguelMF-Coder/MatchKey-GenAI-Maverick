# ADR-003: Graphify and AI Context

## Decision

Use Graphify as the structural knowledge layer for the repository and keep a layered AI context under `docs/00_ai_context/`.

## Current artifacts

- `graphify-out/graph.json`
- `graphify-out/manifest.json`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`

## Why this helps

- It gives future agents a graph-first navigation path.
- It reduces the need to inspect raw files blindly.
- It preserves an honest separation between extracted facts and inferred relationships.
- It supports incremental repo understanding without touching runtime code.

## Limitations

- The graph is only as current as the last extraction run.
- Some nodes or relationships can be inferred rather than directly extracted.
- Generated outputs should be versioned selectively so the repo does not accumulate unnecessary cache noise.

## How future agents should use it

1. Read the AI context files first.
2. Query Graphify before broad file exploration.
3. Use raw source only for confirmation or implementation work.
4. Keep documentation honest about stub and pending areas.
