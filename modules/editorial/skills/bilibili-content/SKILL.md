---
name: bilibili-content
description: Adapt an exact BaseContent revision into a native Bilibili video ChannelContent plan. Use only after platform-neutral content semantics exist. Preserve Core and BaseContent dependencies while designing a complete long-form understanding path; never create Shell, Title, Opening, Thumbnail, or a Xiaohongshu derivative.
---

# Bilibili Content

Read `../../theory/editorial-theory.md` and `../../theory/channel-adaptation-theory.md` completely.

Require the current Core and BaseContent paths from the project snapshot plus `channel=bilibili`, `format=video`. Reject mismatches; never reconstruct BaseContent from Core locally.

## Procedure

1. Choose the BaseContent units the video can responsibly cover; record coverage and omissions.
2. Preserve dependency order while allowing a complete problem → mechanism → evidence → application → boundary arc.
3. Assign each section one understanding change, supporting material, and production treatment.
4. Use examples, visual demonstrations, comparisons, and pauses where they lower reasoning cost.
5. Define `opening_handoff` as the point where an upstream Bilibili ChannelShell opening enters the body; do not write that opening.
6. Place uncertainty and `not_claiming` where viewers might overgeneralize.
7. Save the result to `channels/bilibili-video/content.md`; return the artifact path and references to Workflow for status registration. Do not edit the project snapshot..

Do not compress the plan into Xiaohongshu units, add retention tricks, or create a second hook inside the body.


