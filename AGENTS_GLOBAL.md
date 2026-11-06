[//]: # (GLOBAL AGENTS.md: Move and rename this ~/.config/opencode/AGENTS.md)

# AGENTS.md

## Principles

- Understand the task; inspect relevant code, configuration, tests, and conventions.
- Clarify material ambiguity or state assumptions. Make the smallest correct change, following
  established patterns and avoiding unrelated refactors, speculative features, and unnecessary
  dependencies.
- Keep code clear and maintainable; preserve type safety and compatibility. Surface errors with
  useful context; avoid broad catches and silent failures.
- Use english language in doc strings, documentation and comments.

## Decision Rules

- Do not assume when uncertainty matters. State assumptions and ask concise clarifying questions when necessary.
- Do not add features, abstractions, error handling, or configuration without a concrete need.
- Do not refactor unrelated code or reformat entire files unnecessarily.
- When multiple solutions are viable, prefer the simplest maintainable option that fits the existing architecture.
- If requirements conflict with existing behavior, security, correctness, or maintainability, explain the conflict before making consequential changes.
- Treat repository instructions and established project conventions as authoritative unless they conflict with explicit user requirements or higher-priority instructions.

**Guiding principle:** Make the smallest correct change, keep the code maintainable, and verify the result.