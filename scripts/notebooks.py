"""Explicit Kaggle notebook operations; no action happens on module import."""
import argparse
import json
from pathlib import Path
from common import COMPETITION, ROOT, RUNS, write_json
from kaggle_client import api_client, plain


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file", type=Path)
    subparsers = parser.add_subparsers(dest="action", required=True)
    push = subparsers.add_parser("push")
    push.add_argument("--folder", type=Path, default=ROOT / "notebooks/submission")
    push.add_argument("--timeout", type=int, default=43200)
    push.add_argument("--accelerator")
    for name in ("status", "logs", "output"):
        child = subparsers.add_parser(name)
        child.add_argument("kernel", help="owner/notebook-slug")
        if name == "output":
            child.add_argument("--folder", type=Path, required=True)
    subparsers.add_parser("submissions")
    subparsers.add_parser("quota")
    args = parser.parse_args()
    api = api_client(args.credentials_file)
    if args.action == "push":
        result = plain(api.kernels_push(str(args.folder), timeout=str(args.timeout), acc=args.accelerator))
        write_json(RUNS / "notebooks" / f"{args.folder.name}_push.json", result)
    elif args.action == "status":
        result = plain(api.kernels_status(args.kernel))
    elif args.action == "logs":
        logs = api.kernels_logs(args.kernel)
        path = RUNS / "notebooks" / (args.kernel.replace("/", "__") + ".log")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(logs, encoding="utf-8")
        result = {"saved_log": str(path)}
    elif args.action == "output":
        result = plain(api.kernels_output(args.kernel, str(args.folder), quiet=True))
    elif args.action == "submissions":
        result = plain(api.competition_submissions(COMPETITION))
    else:
        result = plain(api.quota_view())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
