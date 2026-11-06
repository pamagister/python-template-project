# AGENTS_GIT.md

## Purpose

Define consistent Git and GitHub interaction rules for development agents.

## General Principles

- Never overwrite unrelated user changes.
- Never discard uncommitted changes without explicit authorization.
- Inspect `git status` before modifying staging or committing.
- Never use `git add -A` or `git add .` indiscriminately.
- Stage only files belonging to the current task.
- Do not amend existing commits unless explicitly requested.
- Do not force-push unless explicitly authorized.
- Do not commit secrets, credentials, tokens or generated temporary files.
- Use GitHub CLI (`gh`) for GitHub issues, pull requests and Actions where appropriate.

## Commit Messages

Use Conventional Commits. 
Append the issue number to the footer of the commit message when applicable. Use the following format:

```text
<type>(<scope>): <description>

<optional body>
  
<optional footer(s), e.g. `#<number>` for a github issue or `Fixes #` if the issue is completed on this commit>  
```

Common types:

- `feat`: New functionality
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Tests
- `docs`: Documentation
- `build`: Build and dependencies
- `ci`: Continuous integration
- `chore`: Maintenance

Examples:

```text
feat(inventory): add deterministic tree hashing
fix(copy): prevent accidental destination overwrite
test(safety): cover symlink traversal
docs(cli): document inventory options
```

Keep messages concise and describe the actual change.

## GitHub Issues

When requested:

- Search for an appropriate existing open issue first.
- Reuse an existing issue if it accurately describes the work.
- Otherwise create a new issue using `gh issue create`.
- Reference the issue in related commits using `#<issue-number>`.
- Do not create redundant issues.
- Do not close issues merely because a commit was created.

## GitHub Actions

After pushing:

1. Identify the workflow runs associated with the pushed commit.
2. Monitor the relevant CI workflows.
3. Inspect failed jobs and logs.
4. Fix failures before proceeding with dependent implementation work.
5. Confirm successful completion using the actual GitHub Actions status.

Useful commands:

```bash
gh run list
gh run view <run-id>
gh run watch <run-id>
gh issue list
gh issue view <issue-number>
```

Never assume that a successful local test run means GitHub Actions passed.
