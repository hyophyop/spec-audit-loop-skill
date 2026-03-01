#!/usr/bin/env python3
"""Rejudge requirement progress from requirement/audit/gray-box/evidence artifacts.

Purpose:
- Downgrade inflated DONE states when audit evidence is insufficient.
- Recompute progress with formula: (DONE + 0.5 * PARTIAL) / TOTAL * 100.
- Emit deterministic JSON report for docs/CI synchronization.

Input files can be JSON (recommended) or YAML (optional if PyYAML installed).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

STATUS_DONE = "DONE"
STATUS_PARTIAL = "PARTIAL"
STATUS_PENDING = "PENDING"
VALID_STATUSES = {STATUS_DONE, STATUS_PARTIAL, STATUS_PENDING}

WIRING_WIRED = "WIRED"
WIRING_PARTIAL = "PARTIALLY WIRED"
WIRING_UNWIRED = "UNWIRED"

REQUIRED_EVIDENCE_KEYS = (
    "req_id",
    "spec_ref",
    "code_ref",
    "test_ref",
    "test_result",
    "audit_ref",
    "graybox_ref",
    "updated_at",
)


class InputFormatError(RuntimeError):
    """Raised when artifact input format is invalid."""


@dataclass
class ReqResult:
    req_id: str
    from_status: str
    to_status: str
    audit_status: Optional[str]
    graybox_wiring: Optional[str]
    graybox_blocking: bool
    evidence_complete: bool
    reasons: List[str]


def _normalize_status(value: Any) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip().upper()
    if v in VALID_STATUSES:
        return v
    return None


def _normalize_wiring(value: Any) -> Optional[str]:
    if value is None:
        return None
    v = str(value).strip().upper().replace("_", " ")
    if v == "WIRED":
        return WIRING_WIRED
    if v in {"PARTIALLY WIRED", "PARTIAL", "PARTIALLY_WIRED"}:
        return WIRING_PARTIAL
    if v in {"UNWIRED", "NOT WIRED"}:
        return WIRING_UNWIRED
    return None


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "block", "blocking"}
    return False


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputFormatError(f"Input file not found: {path}") from exc


def _load_structured_file(path: pathlib.Path) -> Any:
    text = _read_text(path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise InputFormatError(f"Invalid JSON in {path}: {exc}") from exc

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise InputFormatError(
                f"YAML input requires PyYAML: pip install pyyaml (file: {path})"
            ) from exc
        try:
            return yaml.safe_load(text)
        except Exception as exc:  # pylint: disable=broad-except
            raise InputFormatError(f"Invalid YAML in {path}: {exc}") from exc

    raise InputFormatError(
        f"Unsupported input extension for {path}. Use .json (recommended) or .yaml/.yml"
    )


def _extract_rows(payload: Any, filename: str) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = payload.get("requirements")
        if rows is None:
            # Backward compatible aliases
            for key in ("items", "rows", "data"):
                if isinstance(payload.get(key), list):
                    rows = payload[key]
                    break
    else:
        rows = None

    if not isinstance(rows, list):
        raise InputFormatError(
            f"{filename}: expected a list or an object containing 'requirements' list"
        )

    normalized: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise InputFormatError(f"{filename}: row {idx} is not an object")
        normalized.append(row)
    return normalized


def _index_by_req(rows: Iterable[Dict[str, Any]], filename: str) -> Dict[str, Dict[str, Any]]:
    indexed: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        req_id = row.get("req_id") or row.get("id")
        if not _is_non_empty(req_id):
            raise InputFormatError(f"{filename}: row missing req_id/id")
        key = str(req_id).strip()
        indexed[key] = row
    return indexed


def _evidence_complete(row: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    if row is None:
        return False, ["missing evidence row"]

    missing = [k for k in REQUIRED_EVIDENCE_KEYS if not _is_non_empty(row.get(k))]
    reasons = []
    if missing:
        reasons.append("missing evidence keys: " + ", ".join(missing))

    test_result = str(row.get("test_result", "")).strip().lower()
    if test_result and test_result != "pass":
        reasons.append(f"test_result is not pass ({test_result})")

    return len(reasons) == 0, reasons


def _downgrade_target(
    current_status: str,
    audit_status: Optional[str],
    wiring: Optional[str],
    blocking: bool,
    evidence_complete: bool,
    evidence_reasons: List[str],
    allow_upgrade: bool,
) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    target = current_status

    if audit_status is None:
        reasons.append("missing audit status")
    elif audit_status in {STATUS_PARTIAL, STATUS_PENDING}:
        target = audit_status
        reasons.append(f"audit status is {audit_status}")

    if blocking:
        if target == STATUS_DONE:
            target = STATUS_PARTIAL
        reasons.append("gray-box reports blocking issue")

    if wiring is None:
        if target == STATUS_DONE:
            target = STATUS_PARTIAL
        reasons.append("missing gray-box wiring classification")
    elif wiring != WIRING_WIRED:
        if target == STATUS_DONE:
            target = STATUS_PARTIAL
        reasons.append(f"gray-box wiring is {wiring}")

    if not evidence_complete:
        if target == STATUS_DONE:
            # If evidence is weak but there is some signal, prefer PARTIAL.
            target = STATUS_PARTIAL if current_status != STATUS_PENDING else STATUS_PENDING
        reasons.extend(evidence_reasons)

    done_conditions = (
        audit_status == STATUS_DONE
        and not blocking
        and wiring == WIRING_WIRED
        and evidence_complete
    )

    if current_status != STATUS_DONE and done_conditions and allow_upgrade:
        target = STATUS_DONE
        reasons.append("upgraded by allow-upgrade with complete evidence")

    if current_status == STATUS_PENDING and target == STATUS_PARTIAL:
        # Preserve pending if there is no positive signal at all.
        has_positive_signal = audit_status in {STATUS_DONE, STATUS_PARTIAL} or wiring in {
            WIRING_WIRED,
            WIRING_PARTIAL,
        }
        if not has_positive_signal:
            target = STATUS_PENDING

    if not reasons:
        reasons.append("no status contradiction")

    return target, reasons


def _severity(status: str) -> int:
    if status == STATUS_PENDING:
        return 0
    if status == STATUS_PARTIAL:
        return 1
    return 2


def _progress(results: List[ReqResult]) -> Dict[str, Any]:
    done = sum(1 for r in results if r.to_status == STATUS_DONE)
    partial = sum(1 for r in results if r.to_status == STATUS_PARTIAL)
    pending = sum(1 for r in results if r.to_status == STATUS_PENDING)
    total = len(results)
    percent = ((done + 0.5 * partial) / total * 100.0) if total else 0.0
    return {
        "done": done,
        "partial": partial,
        "pending": pending,
        "total": total,
        "percent": round(percent, 2),
    }


def _render_output(results: List[ReqResult]) -> Dict[str, Any]:
    reopened = [
        {
            "req_id": r.req_id,
            "from": r.from_status,
            "to": r.to_status,
            "reasons": r.reasons,
        }
        for r in results
        if r.from_status == STATUS_DONE and r.to_status != STATUS_DONE
    ]

    rows = [
        {
            "req_id": r.req_id,
            "from_status": r.from_status,
            "to_status": r.to_status,
            "audit_status": r.audit_status,
            "graybox_wiring": r.graybox_wiring,
            "graybox_blocking": r.graybox_blocking,
            "evidence_complete": r.evidence_complete,
            "reasons": r.reasons,
        }
        for r in sorted(results, key=lambda x: x.req_id)
    ]

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "formula": "(DONE + 0.5 * PARTIAL) / TOTAL * 100",
        "summary": _progress(results),
        "reopened": reopened,
        "requirements": rows,
    }


def _write_structured_file(path: pathlib.Path, payload: Any) -> None:
    suffix = path.suffix.lower()
    if suffix == ".json" or suffix == "":
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise InputFormatError(
                f"YAML output requires PyYAML: pip install pyyaml (file: {path})"
            ) from exc
        path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return

    raise InputFormatError(
        f"Unsupported output extension for {path}. Use .json (recommended) or .yaml/.yml"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Rejudge progress from audit/gray-box/evidence artifacts")
    parser.add_argument("--requirements", required=True, help="path to requirement status artifacts")
    parser.add_argument("--audit", required=True, help="path to audit verdict artifacts")
    parser.add_argument("--graybox", required=True, help="path to gray-box verdict artifacts")
    parser.add_argument("--evidence", required=True, help="path to done-evidence artifacts")
    parser.add_argument("--output", help="path to output report (json/yaml). default: stdout")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="apply rejudged status back to requirements file",
    )
    parser.add_argument(
        "--allow-upgrade",
        action="store_true",
        help="allow non-DONE statuses to upgrade to DONE when all conditions pass",
    )
    parser.add_argument(
        "--fail-on-reopen",
        action="store_true",
        help="exit 2 when any DONE is downgraded (useful for CI gate)",
    )

    args = parser.parse_args()

    try:
        req_path = pathlib.Path(args.requirements)
        audit_path = pathlib.Path(args.audit)
        gray_path = pathlib.Path(args.graybox)
        evidence_path = pathlib.Path(args.evidence)

        req_payload = _load_structured_file(req_path)
        audit_payload = _load_structured_file(audit_path)
        gray_payload = _load_structured_file(gray_path)
        evidence_payload = _load_structured_file(evidence_path)

        req_rows = _extract_rows(req_payload, req_path.name)
        audit_rows = _extract_rows(audit_payload, audit_path.name)
        gray_rows = _extract_rows(gray_payload, gray_path.name)
        evidence_rows = _extract_rows(evidence_payload, evidence_path.name)

        req_map = _index_by_req(req_rows, req_path.name)
        audit_map = _index_by_req(audit_rows, audit_path.name)
        gray_map = _index_by_req(gray_rows, gray_path.name)
        evidence_map = _index_by_req(evidence_rows, evidence_path.name)

        all_req_ids = sorted(set(req_map) | set(audit_map) | set(gray_map) | set(evidence_map))
        results: List[ReqResult] = []

        for req_id in all_req_ids:
            base_row = req_map.get(req_id, {})
            audit_row = audit_map.get(req_id, {})
            gray_row = gray_map.get(req_id, {})
            evidence_row = evidence_map.get(req_id)

            from_status = _normalize_status(base_row.get("status")) or STATUS_PENDING
            audit_status = _normalize_status(audit_row.get("status"))
            wiring = _normalize_wiring(gray_row.get("wiring"))
            blocking = _parse_bool(
                gray_row.get("blocking_issue")
                if "blocking_issue" in gray_row
                else gray_row.get("blocking")
            )

            evidence_ok, evidence_reasons = _evidence_complete(evidence_row)
            target, reasons = _downgrade_target(
                current_status=from_status,
                audit_status=audit_status,
                wiring=wiring,
                blocking=blocking,
                evidence_complete=evidence_ok,
                evidence_reasons=evidence_reasons,
                allow_upgrade=args.allow_upgrade,
            )

            # Ensure we do not accidentally upgrade without explicit flag.
            if not args.allow_upgrade and _severity(target) > _severity(from_status):
                target = from_status
                reasons.append("upgrade skipped (allow-upgrade=false)")

            results.append(
                ReqResult(
                    req_id=req_id,
                    from_status=from_status,
                    to_status=target,
                    audit_status=audit_status,
                    graybox_wiring=wiring,
                    graybox_blocking=blocking,
                    evidence_complete=evidence_ok,
                    reasons=reasons,
                )
            )

        report = _render_output(results)

        if args.apply:
            if isinstance(req_payload, dict) and isinstance(req_payload.get("requirements"), list):
                req_list = req_payload["requirements"]
                index = {
                    str((row.get("req_id") or row.get("id"))).strip(): row
                    for row in req_list
                    if isinstance(row, dict) and _is_non_empty(row.get("req_id") or row.get("id"))
                }
                for r in results:
                    if r.req_id in index:
                        index[r.req_id]["status"] = r.to_status
                    else:
                        req_list.append({"req_id": r.req_id, "status": r.to_status})
                req_payload["last_rejudge"] = {
                    "generated_at": report["generated_at"],
                    "summary": report["summary"],
                    "reopened_count": len(report["reopened"]),
                }
                _write_structured_file(req_path, req_payload)
            elif isinstance(req_payload, list):
                index = {
                    str((row.get("req_id") or row.get("id"))).strip(): row
                    for row in req_payload
                    if isinstance(row, dict) and _is_non_empty(row.get("req_id") or row.get("id"))
                }
                for r in results:
                    if r.req_id in index:
                        index[r.req_id]["status"] = r.to_status
                    else:
                        req_payload.append({"req_id": r.req_id, "status": r.to_status})
                _write_structured_file(req_path, req_payload)
            else:
                raise InputFormatError("--apply requires requirements payload to be list or {requirements:[...]}")

        output_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out_path = pathlib.Path(args.output)
            _write_structured_file(out_path, report)
        else:
            sys.stdout.write(output_text)

        if args.fail_on_reopen and report["reopened"]:
            return 2
        return 0

    except InputFormatError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
