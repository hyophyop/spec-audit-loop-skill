---
name: spec-audit-loop
description: Run a spec-first implementation workflow with independent Spark Custom Agent audits, capability/evidence gates, and progress recovery. Use when work must proceed by repeatedly updating/expanding docs/spec/checklists, implementing code, validating with tests, and reconciling roadmap/matrix/gap-log status until requirements reach 100% DONE.
---

# Spec Audit Loop

## Overview

Use this skill to execute a repeatable loop that maximizes traceability and minimizes false completion.
Drive work by requirement IDs, force doc-code-test evidence alignment, and use independent Spark Custom Agent audits to restore real progress status.

Skill contract version:

- `spec-audit-loop@2026.03.01`

Standard artifact path convention:

- Root: `artifacts/spec-audit-loop/`
- Per round: `artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/`
- Required files per round:
  - `audit.json`
  - `graybox.json`
  - `evidence.json`
  - `rejudge.json`
  - `loop-result.md`

Primary objective:

- If there is no blocker that requires user intervention, continue autonomously until current document scope reaches `100%` by the defined progress formula.
- Hand control back to the user only for real blockers (missing credentials/access, destructive decision approval, unavailable required tooling, or ambiguous high-risk product decision).

## Inputs To Lock

Collect and lock these inputs before making edits.

- `phase_doc`: primary requirement document
- `roadmap_doc`: rollout/progress checklist
- `validation_docs`: matrix + gap-log documents
- `req_ids`: requirement IDs for this loop (for example `P8-R01~R07`)
- `test_cmd`: verification command (for example `cargo test --quiet`)

If one input is missing, infer the safest default from repository conventions and record the assumption in the loop summary.

## Bundled Script

Use the bundled script for deterministic progress rejudge.

- Script: `scripts/progress_rejudge.py`
- Purpose: apply Evidence Gate + audit/gray-box contradictions, reopen downgraded requirements, and recompute official progress percentage.
- Recommended artifact format: JSON files with top-level `requirements` list.
- Use this script in every loop after audit results are available.

## Repository Bootstrap (First Use In A Repo)

When this skill is used in a repository for the first time, establish minimal repo-level policy so the workflow remains reproducible.

- Check whether repository `AGENTS.md` exists.
- If missing, create minimal `AGENTS.md` and include a short \"Skill Usage Rules\" section.
- If present but missing policy, append/update only the minimal rules:
  - document-driven implementation/audit/rejudge loop uses `spec-audit-loop`
  - `DONE`/phase completion/`100%` declaration follows this skill's Completion Gate and Auto-Reopen/Rejudge
- Ensure repository policy pins the skill contract version:
  - `spec-audit-loop@2026.03.01`
- Ensure repository policy includes the artifact root:
  - `artifacts/spec-audit-loop/`
- Keep repo policy high-level. Do not duplicate internal implementation details from the skill.
- Perform this bootstrap once per repo, then proceed with the normal loop.

Use the policy snippet template in `references/templates.md`.

## Documentation Bootstrap And Autonomous Expansion

If repository docs are missing or insufficient for this workflow, bootstrap and expand them before claiming progress.

- Required minimum doc set for this skill:
  - `phase_doc` (requirements + acceptance criteria)
  - `roadmap_doc` (progress checklist/status table)
  - `validation_docs` (traceability matrix + gap-log)
- If any required doc is missing, create minimal skeleton files using templates in `references/templates.md`.
- Initialize requirement rows as `PENDING` unless runtime/test evidence already proves at least `PARTIAL`.
- During audit/rejudge, if untracked behavior/constraint/edge-case is discovered:
  - add a new requirement row with deterministic ID
  - add validation matrix link rows and gap-log entries
  - keep new rows as `PENDING` or `PARTIAL` until evidence is complete
- Mark inferred assumptions explicitly as `ASSUMPTION:` in docs and loop report.
- Never hide uncertainty by omitting inferred assumptions.

Autonomous expansion is expected when no blocker-level decision is required.

## Core Loop

Run this loop in order.

1. Verify Spark Custom Agent availability and profile.
2. Apply Capability Gate.
3. Bootstrap/expand docs when needed.
4. Freeze scope in docs.
5. Implement and test.
6. Apply Evidence Gate before status updates.
7. Audit independently with Spark Custom Agent.
8. Run Spark Custom Agent gray-box testing.
9. Reconcile docs to audit verdict.
10. Apply autonomous remediation for obvious audit findings.
11. Recompute progress and next queue.

Repeat until all target requirements are `DONE`.

## Step 0: Verify Spark Custom Agent Availability And Profile

Check whether Spark Custom Agent is available in the current environment before starting the loop.

- Discover current profile from config files when available.
- Read `~/.codex/config.toml` and locate `[agents.spark]` and `config_file`.
- Read the Spark agent config file (for example `~/.codex/agents/spark.toml`) and extract:
  - `model`
  - `model_reasoning_effort`
  - `model_verbosity`
- Ask one explicit profile question before loop start using `references/templates.md`.
- If user selects profile changes, update Spark config file values before spawning agents.
- If Spark Custom Agent is unavailable, ask whether to create it first.
- If user declines creation, continue with local fallback and explicitly mark confidence as reduced.

Never silently skip the independent-audit stage.

## Step 0.5: Apply Capability Gate

Before work starts, validate the auditor profile can handle current scope complexity.

- Define minimum profile for current loop (model family + reasoning effort + verbosity).
- For runtime wiring, rollover routing, or multi-branch state logic, use at least medium reasoning. High is recommended.
- If selected Spark Custom Agent profile is below minimum:
  - Ask user once to upgrade profile.
  - If upgrade is declined, continue with reduced-confidence mode and enforce stricter evidence and one extra local cross-check.
- Never declare `100%` in reduced-confidence mode unless all requirements are re-verified by one additional independent pass.

Use templates in `references/templates.md`.

## Step 1: Freeze Scope In Docs

Update docs before implementation.

- Declare target `req_ids` and acceptance criteria in `phase_doc`.
- Reflect current expected status in `roadmap_doc`.
- Ensure validation matrix rows exist for all target IDs.
- Add missing gaps to gap-log as `Open` if any dependency is not yet wired.

Do not mark `DONE` in this step.

If docs are missing or too sparse to freeze scope, run documentation bootstrap first and then freeze scope.

## Step 2: Implement And Test

Implement only the frozen scope.

- Add or update code paths that satisfy target requirements.
- Add regression tests tied to each requirement.
- Run `test_cmd` and capture pass/fail.
- Fix failures before auditing.

Prefer small, reviewable increments that preserve deterministic test behavior.

## Step 2.5: Apply Evidence Gate Before Status Updates

Enforce evidence completeness before any `DONE` label is written.

- Require a done-evidence record per requirement with:
  - `req_id`
  - `spec_ref`
  - `code_ref` (must include runtime entrypoint->callee chain)
  - `test_ref`
  - `test_result`
  - `audit_ref`
  - `graybox_ref`
  - `updated_at`
- If any required field is missing, force status to `PARTIAL` or `PENDING`.
- Keep evidence rows in validation matrix and ensure links are resolvable.

Use templates in `references/templates.md`.

## Step 3: Run Independent Spark Custom Agent Audit

Spawn Spark Custom Agent as an independent reviewer.

- Ask Spark Custom Agent to classify each `req_id` as `DONE`, `PARTIAL`, or `PENDING`.
- Require concise evidence paths (doc/code/test).
- Ask Spark Custom Agent to report doc-code mismatches.
- Ask Spark Custom Agent for `READY_TO_CONTINUE: yes/no`.
- If Spark sub-agent skills are available, invoke this skill in `MODE=AUDITOR_ONLY`.
- Otherwise, prepend the Spark Auditor Role Card template.
- Save the audit artifact to current round path:
  - `artifacts/spec-audit-loop/round-<timestamp>/audit.json`

Treat Spark Custom Agent output as authoritative for status recovery, then reconcile in Step 4.

Use the prompt template in `references/templates.md`.

## Step 3.5: Run Spark Custom Agent Gray-Box Testing

Run a second independent Spark Custom Agent pass focused on gray-box failures.

- Target runtime entrypoints, state transitions, fallback branches, and schema validators.
- Require at least one boundary or failure-injection scenario per modified runtime path.
- Require explicit finding categories: `Wired`, `Partially Wired`, `Unwired`, `Schema Drift`.
- Force requirement downgrade to `PARTIAL` if gray-box reports critical unwired paths.
- If Spark sub-agent skills are available, invoke this skill in `MODE=GRAYBOX_ONLY`.
- Otherwise, prepend the Spark Gray-Box Role Card template.
- Save the gray-box artifact to current round path:
  - `artifacts/spec-audit-loop/round-<timestamp>/graybox.json`

Use the Spark Custom Agent gray-box prompt template in `references/templates.md`.

## Step 4: Reconcile Docs To Audit

Apply audit verdict to project docs immediately.

- Sync `phase_doc` status table to Spark Custom Agent verdict.
- Sync `roadmap_doc` checklist states.
- Sync validation matrix rows and evidence references.
- Resolve or open gap-log entries according to actual wiring.
- Mark outdated audit docs as superseded and point to latest round.
- Reconcile both audit streams (`Spark Custom Agent Audit`, `Spark Custom Agent Gray-Box`) before final status.

Do not leave parallel conflicting truth sources.

## Step 4.5: Apply Autonomous Remediation For Obvious Findings

When audits report clear and actionable defects, remediate without waiting for a new user turn.

- Expand or correct docs/spec/checklists to capture newly discovered requirements or constraints.
- Add or update validation matrix and gap-log rows for newly surfaced issues.
- Downgrade inflated statuses immediately (`DONE` -> `PARTIAL`/`PENDING`) when evidence is insufficient.
- Re-run focused implementation/tests if remediation changes runtime behavior.
- Trigger one more audit pass after remediation and use the latest pass as the authoritative verdict.
- Expand docs when findings reveal undocumented requirements or constraints.

Only pause for user input when remediation requires a blocker-level decision.

## Step 4.6: Auto-Reopen And Progress Rejudge

When audits find a clear contradiction to current status, reopen immediately.

- If a `DONE` requirement is reported `PARTIAL`/`PENDING`, reopen it and append a new gap-log item.
- Recompute progress with the official formula and publish the downgraded percentage in the same loop report.
- Keep previous verdict as history, but mark it superseded by latest audit round.
- Continue implementation loop automatically unless blocker-level input is required.
- Run the bundled script and store round output:
  - `python3 scripts/progress_rejudge.py --requirements <requirements.json> --audit artifacts/spec-audit-loop/round-<timestamp>/audit.json --graybox artifacts/spec-audit-loop/round-<timestamp>/graybox.json --evidence artifacts/spec-audit-loop/round-<timestamp>/evidence.json --output artifacts/spec-audit-loop/round-<timestamp>/rejudge.json`
  - Optional apply mode: add `--apply` to rewrite requirement statuses in place.
  - Optional CI gate: add `--fail-on-reopen` to fail when any `DONE` is downgraded.

## Step 5: Recompute Progress And Next Queue

Calculate progress with the fixed formula.

- Formula: `(DONE + 0.5 * PARTIAL) / TOTAL * 100`
- Report counts and percentage.
- Publish next queue as only non-`DONE` requirement IDs.

If all target IDs are `DONE`, declare phase progress `100%` and set phase state to completed.
If some IDs are not `DONE` and no blocker exists, continue the loop instead of handing off.

Do not declare `100%` while unresolved `ASSUMPTION:` markers remain in active scope docs.

## Sub-Agent Modes (For Spark Custom Agent)

Use these explicit modes when Spark Custom Agent executes this skill.

- `MODE=AUDITOR_ONLY`
  - Purpose: requirement status audit only.
  - Allowed: read docs/code/tests and produce verdict.
  - Forbidden: code edits, roadmap edits, status inflation, implementation proposals beyond concise findings.
- `MODE=GRAYBOX_ONLY`
  - Purpose: runtime wiring and boundary/failure checks only.
  - Allowed: entrypoint->callee verification, fallback/boundary/schema checks.
  - Forbidden: implementation edits and generic \"looks good\" verdicts without wiring evidence.

If mode is specified, Spark Custom Agent must skip implementation steps and run only relevant audit steps.

## Completion Gate

Mark a requirement `DONE` only when all conditions are true.

- Requirement exists in spec/phase docs.
- Runtime code path exists (not isolated mock-only module).
- Regression test exists and passes.
- Validation matrix row is updated with concrete evidence.
- Independent Spark Custom Agent audit returns `DONE` for that requirement.
- Independent Spark Custom Agent gray-box returns no critical unwired/runtime findings.
- Capability Gate is satisfied (or reduced-confidence compensating checks completed).
- Evidence Gate record is complete.
- No unresolved `ASSUMPTION:` marker for that requirement.

## Runtime Wiring Hard Gate

Apply this gate to prevent the most critical failure mode: implemented modules that never execute in runtime paths.

- Prove at least one production-like entrypoint reaches the new logic.
- Record caller->callee evidence path in docs (for example `runtime -> orchestrator -> scaler`).
- Require one integration or e2e-style test that exercises the wired path through the entrypoint.
- Reject `DONE` if evidence is only module-local unit tests.
- Reject `DONE` if Spark Custom Agent flags \"implemented but unreferenced by runtime\".

If runtime wiring is pending, force status `PARTIAL` and keep an open gap-log item.

## Spark Custom Agent Audit Contract

When requesting Spark Custom Agent audit, require these checks explicitly.

- Detect isolated modules not called from runtime/entrypoint paths.
- Distinguish unit-only coverage from runtime-wired coverage.
- Return one verdict per requirement with direct evidence paths.
- Mark any doc drift where roadmap/phase/matrix disagree.
- Mark missing Spark Custom Agent availability/profile handling as process failure.

Never downgrade this contract to generic \"looks good\" review.

## Spark Custom Agent Role Awareness Contract

When Spark Custom Agent runs audit tasks, enforce auditor identity to reduce role confusion.

- State explicitly: \"You are the auditor, not the implementer.\"
- Require independent judgment from repository evidence, not parent-agent conclusions.
- Provide scope and evidence schema, but do not provide parent verdict labels.
- Require deterministic output format and explicit uncertainty flags when evidence is missing.

Shared rubric is recommended. Shared conclusions are not.

## Spark Custom Agent Gray-Box Contract

When requesting Spark Custom Agent gray-box testing, require these checks explicitly.

- Verify caller->callee runtime reachability from entrypoint.
- Exercise state machine boundaries and transition inversions.
- Inject fallback failures for retry/route logic.
- Validate observability payloads against report validator schema.
- Return hard failures that must block `DONE`.

Never treat gray-box as optional when runtime wiring changed.

## Audit Independence Controls

Maintain independence even if Spark Custom Agent uses the same skill.

- Use shared protocol and templates, but isolate audit inputs from parent-agent conclusions.
- Do not send parent status table to Spark before Spark emits first verdict.
- Store Spark audit artifacts in a separate round folder and reconcile only after both streams complete.
- If one auditor reviewed their own edits, add a second independent pass before completion.

## Guardrails

Apply these guardrails every loop.

- Avoid optimistic status updates before Spark Custom Agent audit.
- Avoid claiming completion from unit-only wiring when runtime path is missing.
- Avoid stale audit artifacts without superseded markers.
- Avoid broad scope creep outside locked `req_ids`.
- Avoid single-source truth in memory; always write reconciled status into phase/roadmap/matrix/gap-log.
- Avoid evidence-free `DONE` labels; every `DONE` must cite code path + test case + audit row.
- Avoid hidden carry-over scope; reset next queue to non-`DONE` IDs only at each loop end.
- Avoid one-audit dependency; require both standard audit and gray-box audit on runtime changes.
- Avoid premature handoff; continue iterating until `100%` unless blocker-level user input is required.
- Avoid unchecked profile drift; re-check Spark Custom Agent profile at each new loop round.
- Avoid stale `100%`; auto-reopen and progress rejudge when new blocking findings appear.
- Avoid silent doc gaps; bootstrap required docs before progressing implementation.
- Avoid assumption leakage; tag and track assumptions until resolved or explicitly accepted.

## Output Contract Per Loop

Return a compact loop report with:

- Implemented items
- Test result summary
- Spark Custom Agent audit/gray-box verdict tables
- Doc reconciliation changes
- `progress_rejudge.py` output summary and reopened list
- Doc bootstrap/expansion actions and active `ASSUMPTION:` list
- Round artifact path and file list
- Updated progress percentage
- Next queue

Use the markdown templates in `references/templates.md`.
