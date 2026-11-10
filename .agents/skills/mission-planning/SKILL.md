---
name: mission-planning
description: Convert a user mission, rough requirements or an external project plan into one concise, executable Markdown implementation plan for an autonomous coding agent.
---

# Mission Planning

Your task is to turn the supplied mission into a clear implementation plan. Do not implement the plan. Write the plan in english.

## Understand the mission

- Identify the objective, expected outcomes, functional and non-functional requirements, constraints, dependencies and risks.
- Separate mandatory scope from optional ideas and explicitly deferred work.
- Identify architectural and interface decisions that materially affect implementation.
- Resolve important ambiguity with the user; do not silently invent product requirements.
- Prefer the simplest design that satisfies the mission.

## Produce one plan

Produce one self-contained Markdown plan, ready to paste into an agent prompt or save at any user-chosen path. Do not require or generate a separate tasklist, progress file or repository instruction file.

Include only sections that add value:
1. Objective and desired outcome.
2. Scope, constraints and explicit non-goals.
3. Architecture and decisions (including rationale where useful).
4. Phases containing coherent work packages.
5. Acceptance criteria and verification expectations.
6. Dependencies, risks and unresolved questions.

## Work-package quality

- Organize work in a logical dependency order.
- Make each work package small enough to implement, review, test and commit independently, but avoid trivial micro-tasks.
- State observable acceptance criteria, not implementation narration.
- Identify integration boundaries and meaningful phase gates.
- Include tests, documentation and migration considerations where relevant.
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

- [ ] P1-W01: Review existing `xxx`, metadata extraction, Python analysis and output models.
- [ ] P1-W02: Define the internal provider interface.
- [ ] P1-W03: Define capability identifiers and capability model.
- [ ] P1-W04: Define the central registry.
- [ ] P1-W05: Define stable error codes and diagnostic references.
- [ ] P1-W06: Update `docs/xxx.md` with the approved architecture.
- [ ] P1-W07: Add focused unit tests for the registry and availability mechanism.

**Acceptance criteria**

- Providers can declare multiple independent capabilities.
- Capability definitions are available centrally.
- Availability checks do not execute file analyses.
- Core modules remain independent of CLI and output formatting.
- Architecture documentation describes the actual agreed design.

**Phase gate:** Do not proceed until the provider and capability interfaces are stable and documented.

### Phase 6 – Documentation, Integration and Quality Assurance

**Objective:** Complete the implementation and ensure consistency across code, documentation and tests.

- [ ] P6-W01: Finalize `docs/....md`.
- [ ] P6-W02: Document the provider and capability architecture.
- [ ] P6-W03: Document all new CLI commands.
- [ ] P6-W04: Document new features.
- [ ] P6-W05: Run the full test suite.
- [ ] P6-W06: Run Ruff, formatting checks and mypy.
- [ ] P6-W07: Run `make precommit`.
- [ ] P6-W08: Build the package and verify optional extras.
- [ ] P6-W09: Perform an end-to-end test with and without optional dependencies and models.

**Acceptance criteria**

- Architecture documentation matches the implementation.
- User documentation contains complete setup instructions.
- CLI help is sufficient to discover the relevant commands.
- Existing functionality remains intact.
- Full test, lint, type-check and build workflows pass.

**Final phase gate:** The implementation is complete only when functionality, tests, CLI help and documentation agree.
```

The plan must be usable whether pasted into a prompt or saved as a Markdown file. Its path is supplied by the user, not assumed.

## Review before delivery

Check that all requirements are represented, dependencies are ordered, acceptance criteria are testable, scope is bounded, and the plan can be executed without unnecessary clarification. Present remaining assumptions and open questions separately from settled decisions.
