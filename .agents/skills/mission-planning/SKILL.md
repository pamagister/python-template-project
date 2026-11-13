---
name: mission-planning
description: Convert a user mission, rough requirements or an external project plan into one concise, executable Markdown implementation plan for an autonomous coding agent.
---

# Mission Planning

Your task is to turn the supplied mission into a clear implementation plan. Do not implement the plan. Write the plan in English.

## Understand the mission

- Identify the objective, expected outcomes, functional and non-functional requirements, constraints, dependencies and risks.
- Separate mandatory scope from optional ideas and explicitly deferred work.
- Identify architectural and interface decisions that materially affect implementation.
- Resolve important ambiguity with the user; do not silently invent product requirements.
- Prefer the simplest design that satisfies the mission.

## When to use this skill

Use this skill when the mission is large, architectural or naturally multi-phase and needs a durable plan for `workflow-autopilot`. For a single self-contained feature or bug fix, use `workflow-feature` and keep the plan lightweight. Do not duplicate repository-wide coding or Git rules in the plan.

## Produce one plan

Produce one self-contained Markdown plan, ready to paste into an agent prompt or save at any user-chosen path. Do not require or generate a separate task list, progress file or repository instruction file.

Include only sections that add value:

1. Objective and desired outcome.
2. Scope, constraints and explicit non-goals.
3. Architecture and decisions (including rationale where useful).
4. Phases containing coherent work packages.
5. Acceptance criteria and verification expectations.
6. Dependencies, risks and unresolved questions.

## Work-package quality

- Organize work in a logical dependency order.
- Give phases and work packages stable identifiers, for example `P1`, `P1-W01`, so Autopilot and commits can reference them.
- Make each work package small enough to implement, review, test and commit independently, but avoid trivial micro-tasks.
- State observable acceptance criteria, not implementation narration.
- Identify integration boundaries and meaningful phase gates.
- Describe the plan content as binding and the order as flexible when Autopilot may combine or reorder phases. Dependencies and acceptance criteria remain binding.
- Include tests, documentation and migration considerations where relevant.
- Use repository-specific verification commands only when they are known; otherwise describe the verification goal and let the implementation agent discover the command.
- Do not prescribe details the implementation agent can safely decide.
- Do not duplicate repository-wide coding or Git rules in the plan.

## Progress-ready format

Put status markers directly in phase and work-package headings:

- `[ ]` pending
- `[-]` in progress
- `[x]` completed
- `[~]` deferred or blocked

Example:

```markdown
## Phase 1: Foundation – Architecture and Data Model

**Objective:** Establish the common architecture before adding additional features.

- [ ] P1-W01: Review existing components, data extraction and output models.
- [ ] P1-W02: Define the internal provider interface.
- [ ] P1-W03: Define capability identifiers and the capability model.
- [ ] P1-W04: Define the central registry.
- [ ] P1-W05: Define stable error codes and diagnostic references.
- [ ] P1-W06: Update the architecture documentation with the approved design.
- [ ] P1-W07: Add focused unit tests for the registry and availability mechanism.

**Acceptance criteria**

- Providers can declare multiple independent capabilities.
- Capability definitions are available centrally.
- Availability checks do not execute file analyses.
- Core modules remain independent of CLI and output formatting.
- Architecture documentation describes the actual agreed design.

**Phase gate:** Verify that the provider and capability interfaces are stable and documented before relying on them in later work.
```

Phase gates are verification checkpoints. Autopilot fixes failures autonomously and interrupts only for a blocker or a critical decision.

## Handoff convention

Autopilot appends a dated `## Progress / Handoff` section at the end of the plan when context is large, at a phase boundary or at completion. The plan author does not need to create this section; leave room for it and do not duplicate it.

The plan must be usable whether pasted into a prompt or saved as a Markdown file. Its path is supplied by the user, not assumed.

## Review before delivery

Check that all requirements are represented, dependencies are ordered, acceptance criteria are testable, scope is bounded, and the plan can be executed without unnecessary clarification. Present remaining assumptions and open questions separately from settled decisions.