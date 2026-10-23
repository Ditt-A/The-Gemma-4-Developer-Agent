"""Refresh one submission result. COMPLETE with an error is a failed evaluation."""
import argparse
import datetime
import json
from pathlib import Path
from common import RUNS, submission_state, write_json
from kaggle_client import api_client, plain


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int)
    parser.add_argument("--credentials-file", type=Path)
    args = parser.parse_args()
    path = RUNS / "state/submission.json"
    receipt = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    saved_id = receipt.get("response", {}).get("ref") or receipt.get("submission", {}).get("ref")
    submission_id = args.id or saved_id
    if not submission_id:
        raise SystemExit("Pass --id or keep the local submission receipt in runs/state/.")
    api = api_client(args.credentials_file)
    from kagglesdk.competitions.types.competition_api_service import ApiGetSubmissionRequest
    request = ApiGetSubmissionRequest()
    request.ref = int(submission_id)
    with api.build_kaggle_client() as client:
        row = plain(client.competitions.competition_api_client.get_submission(request))
    if args.id and saved_id and args.id != saved_id:
        receipt = {}
    receipt.update({"state": submission_state(row), "submission": row,
        "last_checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    write_json(path, receipt)
    print(json.dumps(receipt, indent=2))
    if receipt["state"] == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
