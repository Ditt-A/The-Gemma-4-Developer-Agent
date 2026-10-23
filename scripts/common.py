"""Paths, deterministic packaging and local format checks; no authentication."""
import hashlib
import json
from pathlib import Path
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "agent"
ARTIFACTS = ROOT / "artifacts"
RUNS = ROOT / "runs"
COMPETITION = "gemma-4-developer-agent"
CANDIDATE_ID = "budget-aware-verified-v1"
ALLOWED_EXTENSIONS = {".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}
ALLOWED_MODELS = {
    "gemma-4-31b-it-qat-w4a16-ct", "gemma-4-12b-it-qat-w4a16-ct",
    "gemma-4-e4b-it-qat-w4a16-ct", "gemma-4-e2b-it-qat-w4a16-ct",
}
ROOT_CONFIGS = ("agent.yaml", "agent.yml", "root_agent.yaml", "root_agent.yml")


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_agent_files(agent_dir=AGENT_DIR):
    agent_dir = Path(agent_dir).resolve()
    if not agent_dir.is_dir():
        raise ValueError(f"Agent directory does not exist: {agent_dir}")
    files = {}
    for path in sorted(agent_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed: {path.name}")
        if not path.is_file():
            continue
        if path.suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported submission extension: {path.name}")
        files[path.relative_to(agent_dir).as_posix()] = path.read_bytes()
    roots = [name for name in ROOT_CONFIGS if name in files]
    if len(roots) != 1:
        raise ValueError("The archive needs exactly one root agent configuration")
    if sum(map(len, files.values())) >= 3 * 1024**3:
        raise ValueError("The unpacked submission must be smaller than 3 GiB")
    return files


def load_agent_config(agent_dir=AGENT_DIR):
    """Resolve local includes for packaging. The official compiler is a separate check."""
    agent_dir = Path(agent_dir).resolve()
    files = read_agent_files(agent_dir)

    def load(name, ancestors=()):
        if name in ancestors or len(ancestors) >= 10:
            raise ValueError("Cyclic or overly deep YAML include")
        path = (agent_dir / name).resolve()
        if not path.is_relative_to(agent_dir) or name not in files:
            raise ValueError(f"Include is outside the agent directory: {name}")
        text = files[name].decode("utf-8")
        if path.suffix in (".md", ".txt"):
            return text

        class Loader(yaml.SafeLoader):
            pass

        def include(loader, node):
            reference = loader.construct_scalar(node)
            relative = Path(reference)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Include paths must stay within the agent directory")
            target = (path.parent / relative).resolve()
            if not target.is_relative_to(agent_dir):
                raise ValueError("Include path escapes the agent directory")
            return load(target.relative_to(agent_dir).as_posix(), (*ancestors, name))

        Loader.add_constructor("!include", include)
        return yaml.load(text, Loader=Loader)

    root = next(name for name in ROOT_CONFIGS if name in files)
    agent = load(root)
    if not isinstance(agent, dict) or agent.get("model") not in ALLOWED_MODELS:
        raise ValueError("Declare one supported Gemma 4 model on the root agent")
    generation = agent.get("generate_content_config") or {}
    if not 1 <= generation.get("max_output_tokens", 16384) <= 32768:
        raise ValueError("max_output_tokens must be in 1..32768")
    thinking = generation.get("thinking_config") or {}
    if not 0 <= thinking.get("thinking_budget", 4096) <= 32768:
        raise ValueError("thinking_budget must be in 0..32768")
    return agent


def validate_archive(archive_path, agent_dir=AGENT_DIR):
    expected = read_agent_files(agent_dir)
    load_agent_config(agent_dir)
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("The ZIP failed its CRC check")
        if len(archive.namelist()) != len(expected) or set(archive.namelist()) != set(expected):
            raise ValueError("Archive members differ from the current agent source")
        for name, content in expected.items():
            if archive.read(name) != content:
                raise ValueError(f"Stale or changed archive member: {name}")
    return {
        "candidate": CANDIDATE_ID,
        "archive_sha256": sha256_file(archive_path),
        "archive_bytes": Path(archive_path).stat().st_size,
        "members": {name: hashlib.sha256(value).hexdigest() for name, value in expected.items()},
        "packaging_checks_passed": True,
        "leaderboard_score": None,
        "model_quality_measured_by_this_notebook": False,
    }


def build_bundle(agent_dir=AGENT_DIR, output_dir=ARTIFACTS):
    load_agent_config(agent_dir)
    files = read_agent_files(agent_dir)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / "submission.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    receipt = validate_archive(archive_path, agent_dir)
    write_json(output_dir / "build_receipt.json", receipt)
    return archive_path, receipt


def submission_state(row):
    if row.get("errorDescription") or str(row.get("status", "")).upper() in {"ERROR", "FAILED", "CANCELLED"}:
        return "FAILED"
    if row.get("publicScore") not in (None, ""):
        return "SCORED"
    return "SUBMITTED_AWAITING_RESULT"
