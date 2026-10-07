# Workflow Routing

| Snapshot condition | Next workflow | Skill |
|---|---|---|
| Idea exists; Core missing/draft | `form-core` | `modules/editorial/skills/idea-to-core/SKILL.md` |
| Core confirmed; BaseContent missing | `build-base-content` | `modules/editorial/skills/core-to-base-content/SKILL.md` |
| Core confirmed; BaseShell missing | `build-base-shell` | `modules/editorial/skills/core-to-shell/SKILL.md` |
| BaseContent + Bilibili target | `instantiate-bilibili-content` | `modules/editorial/skills/bilibili-content/SKILL.md` |
| BaseContent + Xiaohongshu target | `instantiate-xiaohongshu-content` | `modules/editorial/skills/xiaohongshu-content/SKILL.md` |
| BaseShell + Bilibili target | `instantiate-bilibili-shell` | `modules/editorial/skills/bilibili-shell/SKILL.md` |
| BaseShell + Xiaohongshu target | `instantiate-xiaohongshu-shell` | `modules/editorial/skills/xiaohongshu-shell/SKILL.md` |
| ChannelShell selected; packaging missing | packaging workflows | packaging Skills |
| Channel content + packaging complete | `compose-script` | `modules/editorial/skills/compose-script/SKILL.md` |
| Confirmed script + assets ready | `direct-visual-story` | `modules/creative/skills/direct-visual-story/SKILL.md` |
| Confirmed direction + request ready | `produce-media` | `modules/production/skills/produce-media/SKILL.md` |
| Current media available | `review-media` | `modules/review/skills/review-media/SKILL.md` |

When a selection is missing, put the specific request in `waiting_for_user`. Candidate lists stay in the conversation; save the selected result only.

Every producing Skill returns its output and references. Only Workflow records the outcome in the project snapshot.
