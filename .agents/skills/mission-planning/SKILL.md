---
name: mission-planning
description: Convert a user mission, rough requirements or an external project plan into one concise, executable Markdown implementation plan for an autonomous coding agent. Include a durable progress and handoff block for session boundaries.
---

# Mission Planning

Turn the supplied mission into a clear implementation plan. Do not implement the plan. Write the plan in English.

## Understand the mission

- Identify objective, expected outcomes, functional and non-functional requirements, constraints, dependencies and risks.
- Separate mandatory scope from optional ideas and explicitly deferred work.
- Identify architectural and interface decisions that materially affect implementation.
- Resolve important ambiguity with the user; do not silently invent product requirements.
- Prefer the simplest design that satisfies the mission.

## When to use

Use this skill when the mission is large, architectural or naturally multi-phase and needs a durable plan for `workflow-autopilot`. For a single self-contained feature or bug fix, use `workflow-feature` and keep the plan lightweight.

## Produce one plan

Produce one self-contained Markdown plan, ready to paste into an agent prompt or save at any user-chosen path. Do not create a separate task list or progress file.

Include only sections that add value:

1. Objective and desired outcome.
2. Scope, constraints and explicit non-goals.
3. Architecture and decisions.
4. Phases containing coherent work packages.
5. Acceptance criteria and verification expectations.
6. Dependencies, risks and unresolved questions.
7. Progress / Handoff block (schema below).

## Work-package quality

- Organize work in dependency order.
- Give phases and work packages stable identifiers, for example `P1`, `P1-W01`.
- Make each work package small enough to implement, review, test and commit independently, but avoid micro-tasks.
- State observable acceptance criteria, not implementation narration.
- Identify integration boundaries and phase gates.
- Include tests, documentation and migration considerations where relevant.
- Use repository-specific verification commands only when known; otherwise describe the goal and let the agent discover the command.
- Do not duplicate repository-wide coding or Git rules in the plan.

## Progress-ready format

Use these status markers directly in headings:

- `[ ]` pending
- `[-]` in progress
- `[x]` completed
- `[~]` deferred or blocked

Example:

```markdown
## Phase 1: Foundation – Architecture and Data Model

**Objective:** Establish the common architecture before adding features.

- [ ] P1-W01: Review existing components and output models.
- [ ] P1-W02: Define the internal provider interface.
- [ ] P1-W03: Add focused unit tests for the registry.

**Acceptance criteria**

- Providers can declare multiple independent capabilities.
- Core modules remain independent of CLI and output formatting.

**Phase gate:** Verify interfaces are stable before later work.
```

## Progress / Handoff block

Every plan must contain this section at the end. It is the durable handoff for compaction or a new session.

```markdown
## Progress / Handoff

- **Mode:** autopilot
- **Plan:** `docs/plans/2026-11-17-example.md`
- **Completed:** P1-W01 (commit abc123, CI green)
- **Active:** P1-W02 `[-]`
- **Next:** P1-W03
- **Relevant files:** `src/foo.py` (lines 120-180), `tests/test_foo.py`
- **Decisions:** ...
- **Blockers:** ...
- **Last verified:** 2026-11-17T08:15Z, `make test` green, CI run 12345 green
- **Context status:** clean | needs-compaction | needs-fresh-session
```

Autopilot updates this block at each phase boundary and before a session handoff. Append a new dated entry rather than rewriting useful history.

## Review before delivery

Check that requirements are represented, dependencies are ordered, acceptance criteria are testable, scope is bounded and the plan can be executed without unnecessary clarification. Present remaining assumptions and open questions separately from settled decisions.