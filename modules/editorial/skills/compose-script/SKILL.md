---
name: compose-script
description: Turn a confirmed channel content plan and selected opening into an evidence-linked narration script and production brief for Creative. Use for explanation videos. Return content changes to Editorial for confirmation; never choose visual style or claim that script approval also approves the visual direction.
---

# Compose a production script

## Required inputs

- Confirmed Core and the channel's content plan.
- The selected channel packaging and opening when one exists.
- Project audience, learning outcome, claims to preserve, uncertainty and delivery constraints.

Stop and report missing prerequisites. Do not reconstruct an absent Core or invent evidence to complete a script.

## Procedure

1. Read the exact referenced content and packaging artifacts. Record their paths and SHA-256 digests.
2. Turn the channel plan into speakable narration. Preserve its claim boundaries, evidence, omissions and uncertainty.
3. Connect the selected opening to the body at an explicit `opening_handoff`; do not write a second hook into the body.
4. For each section, state its learning purpose, narration, evidence references, on-screen facts and what the section must not imply.
5. Flag a proposed factual change or unsupported sentence and return it to Editorial. Do not quietly repair Core meaning.
6. Save the script and `brief.yaml` reference in the project's channel directory.
7. Return artifact paths, digests, unresolved questions and the requested user decision to Workflow. Never edit `project.yaml` or record approval yourself.

## Output

Produce the script and a brief conforming to `modules/editorial/schemas/production-brief.schema.json`. The brief describes content and audience needs; it does not specify style, composition, materials or animation primitives.


