# Workflow Bundle

Context-sparing workflows for OpenCode: task, feature, autopilot and mission planning.

## Skills

- `mission-planning`: turn a mission into one executable plan with a durable handoff block.
- `workflow-task`: bounded change; no commit, push or issue.
- `workflow-feature`: one feature or fix with issue, commit, push and CI.
- `workflow-autopilot`: execute a plan or selected phases with fresh-session handoff.
- `workflow-core`: shared loop, context discipline, safety and verification.
- `git-workflow`: GitHub issues, commits, pushes and CI conventions.

## Use cases

### Mission planning

Run in Plan mode. Produce `docs/plans/<date>-<slug>.md`, no implementation.

```text
@mission-planning

Mission: <rough, multi-phase task>

Create an executable plan at docs/plans/<date>-<slug>.md.
Do not implement.
```

### Task

```text
@workflow-task

<clear bounded change>
```

### Feature

```text
@workflow-feature

Implement <feature>. Reuse or create the issue, commit, push to main, monitor CI.
```

### Autopilot

Start a fresh Build session with the plan and the autopilot skill.

```text
@workflow-autopilot

Execute docs/plans/<date>-<slug>.md.
```

## Plan-to-execution handoff

1. In Plan mode, run `@mission-planning` and write the plan to `docs/plans/...`.
2. Review scope, acceptance criteria and the `## Progress / Handoff` block.
3. Start a new Build session and run `@workflow-autopilot` with the plan path.
4. At phase boundaries or when context grows large, start another fresh session with the updated handoff block.

## Notes

- Use `explore` for broad discovery; avoid full-file reads in the main context.
- Start a fresh session at 60-70% context, after ~120-150 requests, or at a phase boundary.
- Use compaction only when exact recent details matter and do not fit the handoff block.