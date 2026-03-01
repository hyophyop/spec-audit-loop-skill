# AGENTS.md

## Skill Usage Rules (Required)

- This repository follows `spec-audit-loop@2026.03.01`.
- Document-driven implementation/audit/rejudge loops must use the `spec-audit-loop` skill.
- `DONE` promotion, phase completion, and `100%` declaration must follow the skill's Completion Gate and Auto-Reopen/Rejudge rules.
- Official progress and `100%` completion must use repository-wide tracker scope (`global_tracker_doc`); loop progress is supplemental only.
- Standard audit artifact root is fixed to `artifacts/spec-audit-loop/`.

## Issue Tracker Sync Rules (Linear/GitHub)

- Every requirement row must include `source_issue` (for example `GH-123`, `LIN-456`).
- Sync external issue tracker updates at fixed checkpoints only: scope freeze, post-rejudge, and completion declaration.
- External issue close is allowed only when requirement status is `DONE` and Evidence Gate plus both Spark audit streams pass.
- If audit/rejudge downgrades `DONE` to `PARTIAL` or `PENDING`, reopen the linked external issue and add the latest round artifact path.
- Keep one status mapping table in docs and use it consistently.
- For GitHub issue-only workflows, `PENDING` and `PARTIAL` are both `open`; disambiguate with internal tracker status and sync comment checkpoint.

| Internal | GitHub Issue State | GitHub Project Status (if used) | Linear Status |
|---|---|---|---|
| `PENDING` | `open` | `Todo` | `Backlog` or `Todo` |
| `PARTIAL` | `open` | `In Progress` | `In Progress` or `In Review` |
| `DONE` | `closed` | `Done` | `Done` |
