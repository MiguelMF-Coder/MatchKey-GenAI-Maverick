# HR Copilot

## Purpose

Summarize a candidate's interview-style answers into motivations, soft skills, values and preferences.

## Source files

- [backend/app/services/hr_copilot/hr_copilot_tool.py](../../backend/app/services/hr_copilot/hr_copilot_tool.py)
- [backend/app/services/hr_copilot/prompt_templates.py](../../backend/app/services/hr_copilot/prompt_templates.py)
- [backend/app/routers/copilot.py](../../backend/app/routers/copilot.py)

## Current behavior

- `HRCopilotTool.run()` returns a fixed JSON-like dict with motivations, experience highlights, detected values, soft skills, team preferences and a psych summary.
- `BASE_PROMPT` describes the intended shape for a future LLM-backed response.

## Expected JSON

The intended output keys are:

- `motivaciones`
- `experiencia_clave`
- `valores_detectados`
- `soft_skills`
- `preferencias_equipo`
- `resumen_psicologico`

## Current state

- Dummy/stub.
- The response is structurally useful, but it is not powered by a real model yet.

## Integration status

- The copilot router exists in code.
- The main FastAPI app does not currently mount it.
- The Streamlit frontend already prepares UI for this feature, but the live flow is still pending alignment.
