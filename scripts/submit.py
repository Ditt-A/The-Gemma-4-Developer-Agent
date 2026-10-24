"""Submit a verified ZIP explicitly; retain local state to prevent duplicate uploads."""
import argparse
import datetime
import json
from pathlib import Path
from common import AGENT_DIR, ARTIFACTS, CANDIDATE_ID, COMPETITION, RUNS, submission_state, validate_archive, write_json
from kaggle_client import api_client, plain

PENDING_STATES = {"SUBMITTING", "SUBMITTED_AWAITING_RESULT", "NETWORK_UNCERTAIN"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ARTIFACTS / "submission.zip")
    parser.add_argument("--agent-dir", type=Path, default=AGENT_DIR)
    parser.add_argument("--compiler-receipt", type=Path, default=RUNS / "validation/compiler.json")
    parser.add_argument("--candidate-id", default=CANDIDATE_ID)
    parser.add_argument("--description", default="Budget-Aware Verified V1")
    parser.add_argument("--expected-sha256", help="Refuse an archive that differs from this exact SHA-256")
    parser.add_argument("--credentials-file", type=Path)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate locally without authenticating or uploading")
    args = parser.parse_args()
    checked = validate_archive(args.archive, args.agent_dir, candidate_id=args.candidate_id)
    digest = checked["archive_sha256"]
    if args.expected_sha256 and args.expected_sha256 != digest:
        raise SystemExit("Archive SHA-256 does not match --expected-sha256; no upload sent.")
    ledger = RUNS / "state/submission.json"
    old = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else {}
    blocked = old.get("state") in PENDING_STATES or (
        old.get("state") == "SCORED" and old.get("archive_sha256") == digest
    )
    if args.dry_run:
        print(json.dumps({"dry_run": True, **checked, "existing_state": old.get("state"), "duplicate_guard_active": blocked}, indent=2))
        return
    if blocked:
        print("No upload: an existing submission is pending, uncertain, or already scored. Run scripts/status.py to reconcile it.")
        return
    compiler_path = args.compiler_receipt
    compiler = json.loads(compiler_path.read_text(encoding="utf-8")) if compiler_path.exists() else {}
    if not (compiler.get("official_directory_validation") and compiler.get("scripted_adk_integration") and compiler.get("archive_sha256") == digest):
        raise SystemExit("Run scripts/validate_compiler.py on this exact agent before submitting.")
    api = api_client(args.credentials_file)
    description = args.description + " | direct ZIP upload | sha256=" + digest[:16]
    rows = plain(api.competition_submissions(COMPETITION)) or []
    matching = [row for row in rows if row.get("description") == description]
    if matching:
        row = matching[0]
        state = submission_state(row)
        if state != "FAILED" or not args.retry_failed:
            write_json(ledger, {"state": state, "submission": row, "archive_sha256": digest})
            print("Existing submission found; no duplicate sent. A failed result requires --retry-failed after investigation.")
            return
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if old:
        write_json(RUNS / "history" / (timestamp.replace(":", "-") + ".json"), old)
    receipt = {"state": "SUBMITTING", "candidate": args.candidate_id, "route": "direct ZIP upload", "competition": COMPETITION,
        "archive_sha256": digest, "archive_bytes": args.archive.stat().st_size,
        "description": description, "started_utc": timestamp,
        "limits_before": plain(api.competition_get_submission_limits(COMPETITION))}
    write_json(ledger, receipt)
    try:
        response = api.competition_submit(str(args.archive.resolve()), description, COMPETITION, quiet=True)
        receipt["response"] = plain(response)
        if not getattr(response, "ref", 0):
            raise RuntimeError("Kaggle returned no submission id")
        receipt["state"] = "SUBMITTED_AWAITING_RESULT"
    except Exception as exc:
        response = getattr(exc, "response", None)
        status = response.status_code if response is not None else None
        receipt.update({"state": "REJECTED" if status is not None and 400 <= status < 500 else "NETWORK_UNCERTAIN",
            "http_status": status, "error_type": type(exc).__name__,
            "error": response.text[:2000] if response is not None else str(exc)[:1000]})
    finally:
        receipt["last_checked_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_json(ledger, receipt)
        print(json.dumps(receipt, indent=2))
    if receipt["state"] in {"REJECTED", "NETWORK_UNCERTAIN", "FAILED"}:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
