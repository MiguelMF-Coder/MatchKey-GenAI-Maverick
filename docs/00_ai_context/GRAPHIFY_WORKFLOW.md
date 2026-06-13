# Graphify Workflow

## Current state

- Graphify is installed in the project virtual environment at `.venv`.
- The main graph is in `graphify-out/graph.json`.
- A report exists at `graphify-out/GRAPH_REPORT.md`.
- A visual HTML graph exists at `graphify-out/graph.html`.
- There is also a dated snapshot under `graphify-out/2026-06-13/`.

## How an IA should use the graph

1. Start with `graphify-out/graph.json` to understand structure and relationships.
2. Use `graphify query`, `graphify path`, or `graphify explain` before reading many raw files.
3. Read `README.md` only after the graph has oriented you.
4. Fall back to manual file reading only for local verification or when a specific line or module needs confirmation.

## What to version

- Version: `graphify-out/graph.json`.
- Version if you want a human-readable snapshot: `graphify-out/GRAPH_REPORT.md`.
- Version if you want an inspectable visualization: `graphify-out/graph.html`.
- Optional: `graphify-out/manifest.json` if you want provenance metadata.

## What to ignore

- `graphify-out/cache/`
- `graphify-out/.graphify_analysis.json`
- `graphify-out/.graphify_semantic_marker`
- `graphify-out/converted/`
- `graphify-out/20*/` when dated snapshots are only regeneration artifacts

## Pending Graphify work

- Decide whether dated snapshots should stay versioned or be treated as disposable outputs.
- Re-run `graphify update .` after future code changes when the repo changes.
- Expand the graph only when needed for later phases; do not rebuild blindly.
- Keep the graph aligned with the repo commit so the context stays trustworthy.
