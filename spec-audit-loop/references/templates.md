# Spec Audit Loop Templates

## -1) Repository Bootstrap Policy Snippet (AGENTS.md)

```markdown
## 스킬 사용 규칙 (필수)

- 이 저장소는 `spec-audit-loop@2026.03.01` 버전을 기준으로 운영한다.
- 본 저장소의 문서 기반 구현/감사/진척도 재판정 루프는 반드시 `spec-audit-loop` 스킬로 수행한다.
- `DONE` 승격/Phase 완료/100% 선언은 `spec-audit-loop`의 Completion Gate와 Auto-Reopen/Rejudge 규칙을 따른다.
- 공식 진척률 및 100% 완료 기준은 저장소 전역 요구사항(`global_tracker_doc`) 기준으로 판단한다.
- 감사 산출물 표준 루트는 `artifacts/spec-audit-loop/`로 고정한다.

## 이슈 트래커 동기화 규칙 (Linear/GitHub)

- 각 요구사항 행에는 `source_issue`(`GH-123`, `LIN-456` 등)를 필수로 기록한다.
- 외부 이슈 상태 동기화 시점은 `scope freeze`, `post-rejudge`, `completion declaration`으로 고정한다.
- 외부 이슈 종료는 내부 요구사항이 `DONE`이고 Evidence Gate + Spark Audit/Gray-Box가 모두 통과한 경우에만 허용한다.
- Audit/Rejudge에서 `DONE -> PARTIAL/PENDING` 강등이 발생하면 외부 이슈를 즉시 재오픈하고 최신 라운드 산출물 경로를 기록한다.
- 상태 매핑표를 문서에 고정하고 일관되게 사용한다.
- GitHub 이슈 상태만 사용하는 저장소에서는 `PENDING`/`PARTIAL`이 모두 `open`이므로 내부 tracker 상태와 동기화 코멘트로 구분한다.

| Internal | GitHub Issue State | GitHub Project Status (if used) | Linear Status |
|---|---|---|---|
| `PENDING` | `open` | `Todo` | `Backlog` or `Todo` |
| `PARTIAL` | `open` | `In Progress` | `In Progress` or `In Review` |
| `DONE` | `closed` | `Done` | `Done` |
```

## -0.9) Issue Tracker Sync Comment Template

Use when updating GitHub/Linear issues at required checkpoints.

```markdown
### Tracker Sync
- source_issue: <GH-123 | LIN-456>
- checkpoint: <scope-freeze | post-rejudge | completion-declaration>
- internal_status: <PENDING | PARTIAL | DONE>
- github_issue_state: <open | closed>
- github_project_status: <Todo | In Progress | Done | n/a>
- linear_status: <Backlog | Todo | In Progress | In Review | Done | n/a>
- evidence:
  - spec: <path#section>
  - code: <entrypoint -> callee path>
  - test: <file::case + pass/fail>
  - audit: <round audit path>
  - graybox: <round graybox path>
- reopen_reason: <if downgraded>
```

## -0.5) Documentation Bootstrap File Set Template

Use when required docs are missing.

`phase_doc.md`
```markdown
# Phase Requirements

## Scope
- 목표:
- 비목표:

## Requirements
| Req ID | Title | Status | Acceptance Criteria |
|---|---|---|---|
| R01 | <title> | PENDING | <criteria> |

## Assumptions
- ASSUMPTION: <inferred item>
```

`global_tracker_doc.md`
```markdown
# Global Requirement Tracker

| Req ID | Title | Status | Phase | source_issue | Spec Ref | Last Rejudge | Notes |
|---|---|---|---|---|---|---|---|
| R01 | <title> | PENDING | P1 | GH-123 / LIN-456 | phase_doc.md#requirements | - | - |
```

`roadmap_doc.md`
```markdown
# Roadmap

## Checklist
- [ ] R01

## Status
| Req ID | Status | Evidence |
|---|---|---|
| R01 | PENDING | - |
```

`validation_matrix.md`
```markdown
# Validation Matrix

| Req ID | Spec Ref | Code Ref | Test Ref | Audit Ref | Graybox Ref | Status |
|---|---|---|---|---|---|---|
| R01 | phase_doc.md#requirements | - | - | - | - | PENDING |
```

`gap_log.md`
```markdown
# Gap Log

| Gap ID | Req ID | Finding | Severity | Status | Owner |
|---|---|---|---|---|---|
| G01 | R01 | Initial bootstrap gap | Medium | Open | Agent |
```

## -0.4) Assumption Resolution Note Template

```markdown
## Assumption Resolution
- ASSUMPTION: <text>
- Resolution: <resolved|accepted|needs-user-decision>
- Evidence: <doc/code/test path>
- Impacted Req IDs: <list>
```

## 0) Spark Custom Agent Availability Question Template

```text
Spark Custom Agent 설정이 없습니다. 지금 생성할까요?
```

## 0.5) Spark Custom Agent Profile Question Template

```text
현재 Spark Custom Agent 프로파일을 확인했습니다.
- model: <MODEL>
- reasoning: <REASONING_EFFORT>
- verbosity: <VERBOSITY>

감사/그레이박스에 사용할 프로파일을 선택해주세요.
1) 현재 설정 유지
2) 모델 변경 (<NEW_MODEL>)
3) 추론 강도 변경 (<minimal|low|medium|high|xhigh>)
4) verbosity 변경 (<low|medium|high>)
```

## 0.6) Capability Gate Question Template

```text
이번 범위(<REQ_IDS>)는 런타임 배선/롤오버/상태전이 검증이 포함되어 최소 추론 강도는 <MIN_REASONING> 입니다.
현재 Spark Custom Agent 추론 강도는 <CURRENT_REASONING> 입니다.
프로파일을 상향할까요? 상향하지 않으면 reduced-confidence 모드로 진행하고 추가 교차검증을 강제합니다.
```

## 1) Spark Custom Agent Auditor Role Card Template

```text
You are the auditor, not the implementer.
Mode: AUDITOR_ONLY
Rules:
- Use repository evidence only.
- Do not edit code/docs.
- Do not trust parent-agent verdict labels.
- Return explicit uncertainty when evidence is missing.
Output must follow the requested status/evidence schema.
```

## 1.1) Spark Custom Agent Audit Prompt Template

```text
Audit requirement progress for this repo using code evidence only.
Scope: <REQ_IDS>
Read: <PHASE_DOC>, <ROADMAP_DOC>, <VALIDATION_DOCS>, and relevant src/tests.
Output:
1) status table with DONE/PARTIAL/PENDING per requirement + concise evidence paths
2) doc-code mismatches
3) runtime wiring check: detect modules implemented but not reached from runtime entrypoints
4) obvious actionable findings that can be remediated without user input
5) verdict READY_TO_CONTINUE yes/no
Keep concise and evidence-based.
```

## 1.4) Spark Custom Agent Gray-Box Role Card Template

```text
You are the gray-box auditor, not the implementer.
Mode: GRAYBOX_ONLY
Rules:
- Validate runtime entrypoint -> callee wiring with evidence.
- Focus on boundaries, failure-injection, and schema drift.
- Do not patch implementation or claim DONE.
Output must follow the requested wiring/finding schema.
```

## 1.5) Spark Custom Agent Gray-Box Prompt Template

```text
Run gray-box testing for modified requirements using code evidence.
Scope: <REQ_IDS>
Read: runtime entrypoints, state machines, fallback routes, observability validator, and related tests.
Output:
1) per-requirement wiring classification: Wired / Partially Wired / Unwired
2) boundary/failure-injection findings with evidence paths
3) schema-drift findings for logs/report validation
4) obvious remediation actions that can be applied immediately
5) blocking issues that must prevent DONE
Keep concise and evidence-based.
```

## 1.6) Done Evidence Schema Template

```yaml
req_id: <REQ_ID>
spec_ref: <phase_doc#section or requirement row>
code_ref: <entrypoint -> orchestrator -> module path>
test_ref: <test file::case>
test_result: <pass|fail>
audit_ref: <audit artifact path or table row>
graybox_ref: <gray-box artifact path or table row>
updated_at: <ISO-8601 timestamp>
```

If any field is missing, status cannot be `DONE`.

## 1.7) Progress Rejudge CLI Template

```bash
mkdir -p artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>
python3 scripts/progress_rejudge.py \
  --requirements <requirements.json> \
  --audit artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/audit.json \
  --graybox artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/graybox.json \
  --evidence artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/evidence.json \
  --output artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/rejudge.json \
  --apply \
  --fail-on-reopen
```

Use `--apply` only when you want in-place status rewrite.
Use `--fail-on-reopen` for CI-style hard gate.

## 1.8) Progress Rejudge Input Schema Templates

Artifact round directory example:
`artifacts/spec-audit-loop/round-20260301-163000/`

`requirements.json`
```json
{
  "requirements": [
    { "req_id": "P8-R01", "status": "DONE" }
  ]
}
```

`audit.json`
```json
{
  "requirements": [
    { "req_id": "P8-R01", "status": "PARTIAL" }
  ]
}
```

`graybox.json`
```json
{
  "requirements": [
    {
      "req_id": "P8-R01",
      "wiring": "Unwired",
      "blocking_issue": true
    }
  ]
}
```

`evidence.json`
```json
{
  "requirements": [
    {
      "req_id": "P8-R01",
      "spec_ref": "docs/phase-8.md#p8-r01",
      "code_ref": "src/runtime.py -> src/rollover.py",
      "test_ref": "tests/test_rollover.py::test_live_transition",
      "test_result": "pass",
      "audit_ref": "artifacts/audit-round-07.json",
      "graybox_ref": "artifacts/graybox-round-07.json",
      "updated_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```

## 2) Loop Result Template

```markdown
# Loop Result (<date>)

## Artifact Round
- Root: `artifacts/spec-audit-loop/`
- Round: `artifacts/spec-audit-loop/round-<YYYYMMDD-HHMMSS>/`
- Files: `audit.json`, `graybox.json`, `evidence.json`, `rejudge.json`, `loop-result.md`

## Implemented
- <item>

## Tests
- Command: `<test_cmd>`
- Result: <pass/fail>

## Spark Custom Agent Audit Verdict
| Req | Status | Evidence |
|---|---|---|
| <req> | <DONE/PARTIAL/PENDING> | <paths> |

READY_TO_CONTINUE: <yes/no>

## Spark Custom Agent Gray-Box Verdict
| Req | Wiring | Blocking Issue | Evidence |
|---|---|---|---|
| <req> | <Wired/Partially Wired/Unwired> | <yes/no> | <paths> |

## Reconciled Docs
- <phase_doc updates>
- <roadmap updates>
- <validation/gap-log updates>

## Autonomous Remediation Applied
- <issue -> doc/code fix>
- <status downgrade or upgrade reason>

## Auto-Reopen / Rejudge
- <reopened req and reason>
- <superseded verdict reference>
- <progress_rejudge output path>

## Progress
- DONE: <n>
- PARTIAL: <n>
- PENDING: <n>
- Percent: `<value>%`

## Next Queue
1. <req>
2. <req>
```

## 3) Requirement Done Checklist

- Spec requirement row exists.
- Runtime path is wired.
- Regression test exists and passes.
- Validation matrix evidence is updated.
- Spark Custom Agent audit verdict is DONE.
- Spark Custom Agent gray-box has no blocking issue.
