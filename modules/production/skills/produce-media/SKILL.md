---
name: produce-media
description: Prepare narration timing and subtitles, render confirmed Creative requests, assemble project-owned media and probe the actual output. Use when an approved visual direction and project assets are ready. Never invent source audio or alter the confirmed visual plan.
---

# Produce project media

1. Read the confirmed ProductionRequest and its current input fingerprints.
2. Use creator-provided audio. If it is absent, mark the step blocked or continue only with a clearly labelled silent preview.
3. Check the exact script and timing references; do not claim word timing from segment timing.
4. Render shots in Creative order, preserving existing approved candidates.
5. Assemble the requested shots, audio and subtitles. A short audio track is padded to the video duration; do not silently truncate the video.
6. Probe the real output and report dimensions, frame rate, frame count, duration and audio presence.
7. Return artifact paths, input fingerprints and any failures to Workflow. Do not edit `project.yaml` or approve delivery.
