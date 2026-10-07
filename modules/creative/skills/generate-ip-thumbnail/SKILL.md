---
name: generate-ip-thumbnail
description: Generate a finished platform-native cover from an exact confirmed Core revision and human-selected ChannelShell, with optional selected title context and creator portrait. Use only after channel adaptation and selection. Preserve personal-IP identity, keep cover design independent from Shell theory, and directly call image generation rather than returning concepts or prompts.
---

# Generate IP Thumbnail

Generate the final cover image. Do not turn this task into a design consultation.

## Inputs

Require:

- `project_id`
- current confirmed Core path from `project.yaml`;
- current selected ChannelShell path for the target channel;
- `channel` and `format` matching that project channel.

Accept optionally:

- selected title/opening from `packaging.md`, when available, as linguistic context only; never default to rendering its title.
- `self_image`: optional but recommended creator portrait or photo.

Read the Core and selected ChannelShell from the project paths. Reject BaseShell inputs and mismatched channel/format. Do not infer, replace, or improve the ChannelShell from a title or summary.

## Shell Theory

Read [../../theory/shell-theory.md](../../theory/shell-theory.md) and `../../theory/channel-adaptation-theory.md` before generation. They are canonical. Derive the thumbnail from the selected ChannelShell, not from title wording or the abstract Core.

## Shell-First Thumbnail Logic

Perform this process silently:

```text
confirmed Core + selected ChannelShell
→ verify reference compatibility
→ extract the strongest subject + object + relation from the Shell
→ design a thumbnail around that visible relationship
→ generate the final image
```

From the Shell, identify:

- `primary_subject`: the most recognizable content-native person or object;
- `secondary_object`: only a real object needed for comparison or meaning;
- `human_object_relation`: using, holding, comparing, observing, operating, reading, testing, thinking with, confronting, or being surrounded by;
- `object_object_relation`: contrast, competition, sequence, replacement, scale, or dependency;
- `concrete_scene`: the real situation in which the relation becomes visible;
- `visible_conflict`: an anomaly, pressure, opposition, mismatch, or transformation visible without explanation;
- `spatial_relation`: foreground/background, near/far, facing, surrounding, crossing, entering, separating, or converging;
- `information_environment`: documents, screens, notes, search results, data, or interfaces only when they are genuine to the summary.

Choose the visual idea in this strict priority:

1. concrete scene from the Shell;
2. human-object relation;
3. object-object relation;
4. visible conflict;
5. spatial relation;
6. information environment or context;
7. abstract metaphor, only when every concrete option is insufficient.

Do not stop at finding a visible object. Find the strongest visible **object + relation**. Avoid directly illustrating the Core whenever a concrete Shell exists.

Examples:

- For an iPhone review, show the creator holding and comparing two phones—not a phone alone and not the review conclusion.
- For AI learning, show a person actively processing many answers, sources, or questions—not a glowing brain.
- For a tool comparison, place the two real tools, interfaces, or objects in an unmistakable use, contrast, or competition—not two logos floating side by side.

## Compose and Generate

1. Source every meaningful object from the summary. Prefer named phones, books, papers, NotebookLM, documents, AI conversations, notes, whiteboards, data, search results, and other genuine content objects. Do not introduce an unrelated prop merely because it looks attractive.
2. Build one thumbnail-readable composition with one dominant focal relationship. Use at most one main person, one main object, one comparison object when necessary, and minimal context.
3. When `self_image` is present, preserve recognizable facial identity and assign the creator at least one semantic role: user, comparer, observer, operator, reader, thinker, person surrounded by information, person facing an object, or participant interacting with another subject.
4. Adapt pose, gaze, hands, scale, crop, depth, and placement to the relation. Never mechanically cut out the creator and put them on the right while reserving the left for content.
5. Compose the generation instruction internally and call the available image-generation tool directly.
6. Inspect the result. Regenerate when the Shell is no longer visible, the focal relationship is unclear at thumbnail size, identity drifts, unrelated objects appear, accidental text dominates, or constraints are violated.
7. Return the finished image with at most a minimal completion note.

Save the accepted asset path and minimal generation metadata in the channel's `packaging.md`. User acceptance is reflected in `project.yaml`; do not create a separate Decision Record.

Do not expose the inferred Core, inferred Shell, intermediate reasoning, candidate concepts, generation prompt, title options, design explanation, or checklist unless explicitly requested.

## Visual Language

Use a modern editorial technology aesthetic: clean, restrained, intelligent, contemporary, high signal-to-noise, thumbnail-readable, and grounded in realistic object rendering or photography. Favor cool gray, black, white, and blue-gray while retaining a subject's natural identifying colors.

Create every episode independently. Maintain series identity through photographic quality, lighting, creator treatment, negative space, information density, composition logic, object photography, and editorial taste—not a fixed layout, repeated pose, fixed filter, or mandatory creator placement.

Use content-native patterns:

- Product or tool review: person + product + use or comparison relation.
- Learning method: person interacting with books, papers, notes, cards, whiteboard, screen, or another real behavior object.
- Research or deep analysis: person or focal evidence interacting with a report, paper, chart, data, or material stack.
- AI or information topic: person with real questions, answers, documents, screens, search results, or tool-specific objects.
- Abstract viewpoint: use a metaphor only after no concrete Shell relationship can carry the idea.

Do not default to brains, robots, AI glows, cyber interfaces, holographic faces, or abstract node networks.

## Title and Text Policy

Keep the cover complementary to the title rather than repetitive. Do not make it explain the full content, carry the conclusion, restate the title, or turn the title into a poster.

Default to:

- no title;
- no subtitle;
- no big text;
- no labels;
- no decorative text.

Allow only text that naturally belongs to the depicted object or scene: a product logo, device marking, native software UI, or real environmental text. Keep it subordinate.

## Platform Adaptation

- For `bilibili`, create a landscape cover designed for small-feed recognition and safe cropping.
- For `xiaohongshu`, create a portrait-native cover whose action and relation remain clear in the feed.
For two channels, the workflow manager starts two separate runs using their own selected ChannelShells. Never accept `both` as one invocation.

Use the image tool's supported dimensions or closest native aspect ratio. Preserve the same Shell, relationship, and visual language while recomposing scale, negative space, and depth for each platform.

## Hard Constraints

Reject:

- title-as-poster treatment or large added words;
- PPT-like layout, random screenshot collage, gratuitous UI cards, or mechanical split-screen;
- several competing focal points, tiny unreadable objects, or a subject without a meaningful relation;
- generic AI symbolism or an abstract Core visualization when a concrete Shell exists;
- an unrelated creator cutout or decorative prop;
- a fixed person-right/content-left template;
- copying a reference image's exact scene, brand treatment, typography, or composition;
- sacrificing thumbnail readability for novelty.

## References

Read [references/visual-reference-guide.md](references/visual-reference-guide.md) when using the bundled examples. Treat `assets/reference-thumbnails/` as evidence for Shell expression, visible relationships, focal clarity, and series consistency—not as templates or source material to reproduce.
