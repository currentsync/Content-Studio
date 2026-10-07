---
name: manage-content-workflow
description: Start, resume, inspect, and advance a content project using its single project.yaml snapshot and Workflow CLI. Use to determine what is complete, what is missing, which module Skill to call next, when user input is required, and how to register results. Do not perform creative transformations itself.
---

# Manage Content Workflow

Keep orchestration simple: one project snapshot, content files, and one append-only runtime log.

## Required context

Read:

1. `../../../../AGENTS.md`
2. `../../config/workflows.yaml`
3. `../../config/storage.yaml`
4. the project's `project.yaml`
5. [references/routing.md](references/routing.md)

## Resume procedure

1. Open `projects/<project_id>/project.yaml`.
2. Resolve only the current content paths needed for the next step.
3. Read `todo` and `waiting_for_user`.
4. If user input is required, ask for it and stop. Do not infer confirmation or selection.
5. Otherwise call the one Skill mapped to the next workflow in `../../config/workflows.yaml`.
6. The producing module saves its own project-relative artifact using `../../config/storage.yaml`; it returns paths, input references and digests to Workflow.
7. Workflow alone updates `project.yaml`: current paths, channels, `completed`, `todo`, `waiting_for_user`, approvals and `updated_at`.
8. Register the result through the root-relative CLI. A successful artifact result updates the snapshot and rebuilds `projects/index.yaml`:

```powershell
uv run python modules/workflow/scripts/studio.py record --project <id> --operation <workflow> --result succeeded --output <relative-path>
```

For blocking or failure, use `--result blocked|failed --detail "..."`. Runtime is diagnostic only; never read it as the authoritative project state.

Before asking for delivery confirmation, require a validated independent ReviewReport that references the exact current artifact digest and passes with no unresolved blocking finding. Generate a draft with `modules/review/scripts/report.py --create`, have the independent reviewer complete it, and validate it with `--report`. Do not treat technical QA or an old report as approval.

When the user explicitly confirms the current delivery and project completion, record both actual confirmations against the same artifact path and digest, then call `uv run python modules/workflow/scripts/studio.py archive --project <id>`. A new delivery version invalidates a complete confirmation for an older version. Archive rechecks the current artifact digest, passing review, open work, and matching approvals before moving the project.

## Snapshot rules

- Keep one `project.yaml`; only Workflow writes it after meaningful work.
- Keep content in `content/` and `channels/`; do not inline full content into the snapshot.
- Make `todo` concrete and ordered. The first eligible item is normally next.
- Use `waiting_for_user` only for a specific required confirmation or choice; remove it after the user answers.
- Do not create separate state-machine, run-instance, decision-record, or candidate-state files.
- Candidate lists may remain in the conversation until the user chooses; save the selected result.

## Hard boundaries

- Do not perform the creative work owned by another Skill.
- Do not route Core directly to ChannelContent or BaseShell directly to packaging.
- Do not infer Core confirmation, channel/format, BaseShell selection, or ChannelShell selection.
- Do not use runtime logs to reconstruct or override `project.yaml`.
