---
name: review-media
description: Independently review a specific Content Studio media version against its content evidence, Creative direction, narration, visual clarity, captions and delivery requirements. Use after Production emits a candidate. Do not review work you authored or approve a version that has changed since inspection.
---

# Review a media candidate

## Inputs

- The actual media artifact and its SHA-256 digest.
- Current Editorial brief, script and evidence references.
- The user's confirmed Creative direction and project delivery requirements.
- Technical QA output for the same version.

## Review

1. Confirm the file digests match the version being reviewed. Stop if any required input is missing or stale.
2. Inspect the complete media, including transitions and ending. Check whether visuals explain each claim and preserve uncertainty and scope.
3. Check spoken words, figures, captions, reading time, safe areas and actual audio/video duration. Report the timestamp or shot for each issue.
4. Separate measurable technical checks from your editorial and visual judgment. A passing renderer or QA report does not establish factual accuracy.
5. Assign each finding to Editorial, Creative, Production or Workflow, give a blocking flag and a concrete resolution.
6. Pass only when no blocking issue remains and all requested content and delivery checks are covered.
7. Write the ReviewReport for the exact media digest, mark the reviewer independent, and return it to Workflow. Do not edit project state or approve delivery.

When an input changes, review the affected result again. Keep the prior report for history; a report for an older digest cannot approve a newer file.
