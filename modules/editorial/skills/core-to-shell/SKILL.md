---
name: core-to-shell
description: Convert an exact human-confirmed Core into 5–8 platform-neutral BaseShell candidates grounded in familiar problems, scenes, conflicts, anomalies, objects, experiments, or tasks. Use before any Bilibili or Xiaohongshu Shell adaptation; never create ChannelShell, Title, Opening, Thumbnail, or body content.
---

# Core to BaseShell

Read `../../theory/shell-theory.md` and `../../theory/channel-adaptation-theory.md` completely.

Require the project snapshot to point to a confirmed current Core. Stop if it is missing or unconfirmed.

1. Extract the Core's real explanatory claim and audience.
2. Map it to platform-neutral, familiar problems, scenes, anomalies, comparisons, tasks, experiments, or objects.
3. Verify the Core genuinely explains every candidate.
4. Generate 5–8 meaningfully distinct candidates; remove titles, platform styling, paraphrases, trends, and fabricated tension.
5. For each include `candidate_id`, `shell`, `type`, `familiar_problem`, `scene_or_conflict`, `bridge_to_core`, `rationale`, and `risks`.
6. Return concise BaseShell candidates in the conversation without choosing a winner. After the user chooses, save only the selected result to `content/base-shell.md`; return the artifact path and references to Workflow for status registration. Do not edit `project.yaml`..

BaseShell is a mother entrance. Do not optimize it for Bilibili completeness or Xiaohongshu saveability; those are downstream channel decisions.


