"""Rebuild the exact scored Budget-Aware V10 public artifact, without network access."""
import argparse
import hashlib
import json
from pathlib import Path
from common import ROOT, ARTIFACTS, build_bundle, read_agent_files, write_json

MANIFEST = ROOT / "provenance/reproduction_v10.json"
UPSTREAM_DIR = ROOT / "provenance/upstream/budget_aware_v10"


def verify_reference():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    actual = {name: hashlib.sha256(data).hexdigest() for name, data in read_agent_files(UPSTREAM_DIR).items()}
    if actual != manifest["members"]:
        raise ValueError("Upstream source differs from the scored V10 reference")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ARTIFACTS / "reproduction_v10")
    args = parser.parse_args()
    manifest = verify_reference()
    path, receipt = build_bundle(UPSTREAM_DIR, args.output_dir, candidate_id=manifest["candidate_id"])
    if receipt["archive_sha256"] != manifest["archive_sha256"] or receipt["archive_bytes"] != manifest["archive_bytes"]:
        raise ValueError("Rebuilt ZIP differs from the scored public output")
    receipt.update({"exact_public_artifact_reproduced": True, "upstream_url": manifest["upstream_url"],
        "upstream_public_score": manifest["upstream_public_score"]})
    write_json(args.output_dir / "build_receipt.json", receipt)
    print(json.dumps({"archive": str(path), **receipt}, indent=2))


if __name__ == "__main__":
    main()
