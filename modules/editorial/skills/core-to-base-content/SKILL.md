---
name: core-to-base-content
description: "Convert an exact human-confirmed Core Package into platform-neutral BaseContent: knowledge units, dependency order, evidence and case roles, scope boundaries, and uncertainties. Use before any Bilibili or Xiaohongshu content adaptation. Never produce pages, video sections, scripts, Shells, titles, openings, thumbnails, or CTAs."
---

# Core to Base Content

Read `../../theory/editorial-theory.md` and `../../theory/channel-adaptation-theory.md` completely.

Require a project snapshot with `core_status: confirmed` and read its current Core file. Stop when the Core is missing, unconfirmed, contradictory, or unsupported.

## Procedure

1. Preserve `core_statement`, scope, `not_claiming`, and uncertainties verbatim in meaning.
2. Define the audience's current understanding and the minimum learning outcome.
3. Decompose the Core into knowledge units. Give each unit one cognitive job and a stable `unit_id`.
4. Order units by dependency, not by source discovery or platform rhythm.
5. Map evidence, cases, comparisons, and demonstrations to the unit they support; do not let an anecdote carry a general claim.
6. Record exclusions and uncertainty placements.
7. Remove all channel, format, packaging, page, shot, duration, and CTA decisions.
8. Save the result to `content/base-content.md`; return the artifact path and references to Workflow for status registration. Do not edit the project snapshot..

Output compact YAML with `audience_need`, `learning_outcome`, `knowledge_units`, `dependency_order`, `evidence_map`, `case_map`, `exclusions`, and `uncertainties`.

Do not silently narrow the Core to fit a channel. Channel Skills decide coverage later and must cite omitted BaseContent units.


