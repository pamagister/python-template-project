# MISSION_GUIDELINE.md

This document defines how implementation missions must be prepared for autonomous coding agents.
When creating a plan, paste this into the prompt window of the Planner-AI and instruct it to generate the required artifacts.


## Purpose

This document defines how implementation missions must be prepared for autonomous coding agents.

The planner is responsible for translating the user's requirements into a structured, actionable and verifiable implementation plan.

The resulting artifacts must allow an implementation agent to work independently without requiring repeated clarification of architectural decisions or intended functionality.

## 1. Understand the Mission

Before creating implementation artifacts:

- Understand the actual objective and expected outcome.
- Identify functional and non-functional requirements.
- Identify constraints, dependencies and potential risks.
- Distinguish mandatory requirements from optional improvements.
- Identify unresolved architectural decisions.
- Ask clarifying questions when important decisions cannot reasonably be inferred.

Do not introduce unnecessary features or complexity.

## 2. Required Artifacts

For substantial implementation projects, create:

### AGENTS.md

DO ONLY CREATE IF REQUESTED. Otherwise, use the existing `AGENTS.md` file in the project root.

A concise description of:

- Project vision and purpose.
- Architectural principles.
- Technology and development conventions.
- References to specialized instruction files.

### AGENTS_GIT.md

DO NOT CREATE A NEW FILE. Use the existing `AGENTS_GIT.md` file in the project root.

Git and GitHub interaction rules, including:

- Commit conventions.
- Issue management.
- Push strategy.
- GitHub Actions monitoring.

### AGENTS_WORKFLOW.md

DO NOT CREATE A NEW FILE. Use the existing `AGENTS_WORKFLOW.md` file in the project root.

Implementation workflows:

- Standard one-shot implementation.
- Autonomous AUTO Mode.
- Testing and pre-commit procedures.
- Commit, push and CI requirements.
- Progress tracking and completion criteria.

### plan.md

A comprehensive implementation specification containing:

- Project objective.
- Architecture.
- Technology decisions.
- Functional requirements.
- Interfaces and data models.
- Security and quality requirements.
- Proposed project structure.
- Implementation roadmap.
- Definition of Done.
- Explicitly deferred features.

### tasklist.md

A practical implementation checklist:

- Organized by phases and work packages.
- Small enough for independent implementation steps.
- With explicit completion criteria.
- Using `[ ]`, `[-]`, `[x]` and `[~]` status markers.
- Consistent with `plan.md`.

## 3. Planning Principles

- Prefer concrete implementation requirements over vague descriptions.
- Make architectural decisions explicit.
- Avoid over-engineering.
- Separate initial scope from future extensions.
- Define dependencies between implementation phases.
- Make every phase independently testable where possible.
- Include security and error handling in the initial design.
- Ensure that the tasklist reflects the actual implementation sequence.

## 4. AUTO Mode Compatibility

Plans must be suitable for autonomous implementation according to `AGENTS_WORKFLOW.md`.

Therefore:

- Divide work into coherent implementation packages.
- Define clear milestones.
- Make tasks independently verifiable.
- Identify suitable commit boundaries.
- Use one Jira ticket per implementation phase or work package.
- Allow GitHub issue references where requested.
- Include validation requirements before considering a task complete.
- Define conditions for closing implementation phases.

## 5. Quality Review Before Delivery

Before presenting the plan, verify:

- All user requirements are represented.
- No essential architectural decisions remain implicit.
- The project structure is reasonable.
- The implementation phases are logically ordered.
- The tasklist covers the complete initial scope.
- Tests and quality checks are included.
- AUTO Mode can execute the plan without unnecessary interruptions.
- Future extensions are clearly separated from initial requirements.

## 6. Delivery

Present all generated artifacts in Markdown, ready to copy into the project repository.

Explain briefly:

- Important architectural decisions.
- Relevant assumptions.
- Remaining open questions.
- Recommended implementation starting point.

The plan should be detailed enough for autonomous execution but must not prescribe unnecessary implementation details that belong to the coding agent.

**Guiding principle: A good mission is not merely a description of what should be built. It is an executable specification with clear responsibilities, milestones and verifiable outcomes.**