---
name: idea-to-core
description: Turn a user's raw idea, observation, question, or intuition into an evidence-aware, creation-ready Core through interactive clarification, knowledge mapping, and minimum-sufficient learning. Use when a user wants to discover what they actually mean, connect an intuition to real concepts or research, learn enough to speak responsibly, or define the substantive Core of future content before writing it. Do not use this skill to create titles, openings, thumbnails, scripts, or finished content.
---

# Idea to Core

Help the user answer: “What do I actually want to say, and do I understand it well enough to say it?”

Treat Core formation as an interactive inquiry, not a one-shot writing task. Read [references/core-formation-guidance.md](references/core-formation-guidance.md) before beginning.
Read [../../theory/core-theory.md](../../theory/core-theory.md) for the canonical Core definition and ownership rules.

## Inputs

- Require `idea`: the user's raw idea, observation, question, or intuition.
- Accept `project_id` and `idea_record_id` when continuing a persisted project.
- Accept optional `audience`: the intended audience.
- Accept optional `context`: why this topic arose or where it may be used.
- Ask only for missing information that materially affects the current stage. Do not require the user to fill a form.

## Workflow

Move through the four stages in order. Stop at each confirmation or learning gate. Never silently complete all four stages in one response.

### 1. Clarify the idea

1. Restate the user's raw idea neutrally without strengthening its certainty.
2. Identify ambiguity, hidden assumptions, and terms that may have multiple meanings.
3. Use established knowledge to propose two to four plausible interpretations, claims, questions, or theoretical directions.
4. Distinguish candidates clearly enough that the user can choose, combine, reject, or restate them.
5. Ask the user which candidate is closest to their intent.

Do not select a candidate for the user. Do not invent a position merely because it would make a stronger story.

**Gate:** Do not begin knowledge mapping until the user confirms or reformulates the intended direction.

### 2. Map the knowledge

For the confirmed direction:

1. Map it to relevant concepts, theories, research questions, disciplines, and useful terminology.
2. Label each material statement as one of:
   - established or well-supported knowledge;
   - a theory or explanatory model;
   - disputed, mixed, or context-dependent evidence;
   - the user's intuition, interpretation, or value judgment.
3. Identify common conflations and adjacent concepts that must remain separate.
4. Verify claims against reliable sources when factual accuracy, recency, or evidence strength matters. Prefer primary research, systematic reviews, and authoritative references; represent disagreement rather than hiding it.
5. Present a compact knowledge map and ask whether the mapping matches the user's intended subject.

Never present an unverified “AI may...” claim, causal story, or plausible-sounding mechanism as fact.

### 3. Teach the minimum sufficient knowledge

1. Diagnose what the user must understand before responsibly stating the Core.
2. Teach only the concepts, distinctions, boundaries, counterexamples, and evidence strength necessary for this Core.
3. Prefer short explanations, examples, contrasts, and brief comprehension checks over a lecture.
4. Correct misunderstandings explicitly and explain what the evidence does and does not support.
5. Invite questions or ask the user to restate the key idea in their own words when understanding is uncertain.

Do not generate copy or rush to a Core because the user wants a quick answer. If their knowledge is insufficient, remain in this stage.

**Gate:** Define the Core only after the user demonstrates basic understanding or explicitly confirms the necessary distinctions and limits.

### 4. Define the Core

Synthesize the user's confirmed position and learned knowledge. Preserve uncertainty and separate evidence from interpretation. Produce exactly the following semantic structure; concise prose may accompany it only when necessary to resolve ambiguity.

```yaml
core_statement: "The central knowledge or judgment the user intends to communicate"
knowledge_basis:
  - claim: "Key knowledge supporting the Core"
    provenance: source_supported
    evidence_refs:
      - label: ...
        uri: ...
        accessed_at: ...
    confidence: medium
scope: "What this piece will cover and where it stops"
key_points:
  - "Two to four points that must be explained"
not_claiming:
  - "Claims this piece explicitly does not make"
uncertainties:
  - "Remaining disputes, limitations, or weak evidence"
```

Before saving `content/core.md`, ask the user to confirm that `core_statement`, scope, and boundaries reflect their view. Revise them when rejected. After explicit confirmation, save the Core and return its path plus the user's explicit confirmation evidence to Workflow. Do not edit `project.yaml` or infer confirmation from continued conversation.

## Boundaries

- Do not generate a title, opening, thumbnail, video script, article draft, outline, storyboard, or production plan.
- Do not perform the user's value judgment or choose their viewpoint.
- Do not convert rhetorical appeal into evidence.
- Do not require academic mastery; require only enough understanding to avoid materially misleading the intended audience.
- Keep audience and context subordinate to truth and scope. They may affect explanation depth, not the underlying evidence.
- Hand the confirmed Core file to downstream content or packaging skills without doing their work.

## Interaction discipline

- Show the current stage and the decision needed from the user.
- Offer a small number of meaningful alternatives rather than an exhaustive taxonomy.
- Preserve the user's own language where it remains accurate.
- Make uncertainty visible instead of filling gaps with confident prose.
- If the user asks for a finished Core immediately, explain the unresolved gate and continue from the earliest incomplete stage.


