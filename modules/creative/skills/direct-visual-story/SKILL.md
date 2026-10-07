---
name: direct-visual-story
description: Direct the visual explanation for an evidence-grounded production brief. Independently choose a suitable style and media treatment, explain the choice, and return a reviewable plan for user confirmation. Use for video and animated explainers.
---

# Direct visual story

## Required inputs

- An Editorial production brief and its exact source artifacts.
- Available assets with source and allowed-use information.
- Delivery dimensions, duration constraints and any user-provided preferences.

If content claims, evidence or the selected opening are unclear, return the issue to Editorial. Do not invent facts or use example content as evidence.

## Procedure

1. Identify the audience's required understanding change for each section.
2. Choose the visual grammar that explains those changes with available materials. Animation, still images, charts, screenshots and pauses are all valid treatments.
3. Explain why the style fits the content, the material constraints and any tradeoff. Do not force a house style across unrelated explanation tasks.
4. Map each visual unit to a brief section and cite its content references. Mark illustrative numbers, recreated interfaces and demo-only assets as such.
5. Describe shots/pages and required assets at the level needed by Production. Keep style-specific composition and motion choices inside this Creative plan.
6. Ask the user to confirm the overall style and representative visual direction before formal rendering. Return the requested decision to Workflow.
7. After confirmation, produce a `ProductionRequest` for the supported renderer. If the content meaning must change, stop and return it to Editorial.

## Output

Write `creative/plan.yaml` using `modules/creative/schemas/creative-plan.schema.json`, plus the style-specific native project files. Return paths, source digests, material gaps and the confirmation request. Do not update the project snapshot.
