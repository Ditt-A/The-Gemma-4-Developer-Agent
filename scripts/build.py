"""Build artifacts/submission.zip from the editable agent/ directory."""
import argparse
import json
from pathlib import Path
from common import AGENT_DIR, ARTIFACTS, build_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-dir", type=Path, default=AGENT_DIR)
    parser.add_argument("--output-dir", type=Path, default=ARTIFACTS)
    args = parser.parse_args()
    path, receipt = build_bundle(args.agent_dir, args.output_dir)
    print(json.dumps({"archive": str(path), **receipt}, indent=2))


if __name__ == "__main__":
    main()
