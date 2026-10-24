"""Generate self-contained notebooks from agent/ and checked-in cell templates."""
import hashlib
import json
from pathlib import Path
import nbformat
from common import ROOT, AGENT_DIR, CANDIDATE_ID, read_agent_files, load_agent_config


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


def save_notebook(path, cells):
    for index, cell in enumerate(cells):
        cell.id = f"cell-{index:02d}"
        if cell.cell_type == "code":
            compile(cell.source, f"{path.name} cell {index}", "exec")
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"},
    })
    nbformat.validate(notebook)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")


def packaging_cells(agent_dir, intro, candidate_id):
    load_agent_config(agent_dir)
    members = {name: value.decode("utf-8") for name, value in read_agent_files(agent_dir).items()}
    code = nbformat.v4.new_code_cell
    markdown = nbformat.v4.new_markdown_cell
    return [
        markdown(intro),
        code(source("templates/submission/setup.py")),
        code("# Generated from the repository source; regenerate after editing.\nCANDIDATE_ID = " + repr(candidate_id) + "\nFILES = " + repr(members) + "\nEXPECTED_MEMBER_HASHES = " + repr({name: hashlib.sha256(text.encode('utf-8')).hexdigest() for name, text in members.items()}) + "\n"),
        code(source("templates/submission/validate.py")),
        code(source("templates/submission/package.py")),
        markdown("Upload `/kaggle/working/submission.zip` through File Upload or `KaggleApi.competition_submit`. The packaging notebook does not run hidden evaluation. See docs/submission.md for authentication, validation and status checks."),
    ]


def main():
    code = nbformat.v4.new_code_cell
    markdown = nbformat.v4.new_markdown_cell
    package_cells = packaging_cells(AGENT_DIR, source("templates/submission/intro.md"), CANDIDATE_ID)
    save_notebook(ROOT / "notebooks/submission/submission.ipynb", package_cells)
    gpu_cells = [
        markdown("# Gemma 4 31B GPU compatibility check\n\nRun on Kaggle L4x4 with the organizer wheelhouse and model inputs. This checks serving and one tool call, not repair quality. The historical 300-second run expired during checkpoint loading. Choose a runtime that covers setup and model startup."),
        code("import time\nsmoke_started = time.perf_counter()"),
    ]
    gpu_cells += [code(cell.source) for cell in package_cells if cell.cell_type == "code"]
    gpu_cells += [code(source(f"templates/gpu_smoke/{name}.py")) for name in ("install", "serve", "check")]
    save_notebook(ROOT / "notebooks/gpu_smoke/gpu_smoke.ipynb", gpu_cells)
    from reproduce_public import MANIFEST, UPSTREAM_DIR, verify_reference
    verify_reference()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reproduction = packaging_cells(UPSTREAM_DIR, source("templates/reproduction_v10/intro.md"), manifest["candidate_id"])
    reproduction.append(code(
        "# Match the scored public artifact, including the ZIP container bytes.\n"
        f"assert receipt['archive_sha256'] == {manifest['archive_sha256']!r}\n"
        f"assert receipt['archive_bytes'] == {manifest['archive_bytes']!r}\n"
        "receipt['exact_public_artifact_reproduced'] = True\n"
        f"receipt['upstream_url'] = {manifest['upstream_url']!r}\n"
        "(OUTPUT / 'build_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')\n"
        "print('Exact public V10 artifact reproduced. Our leaderboard result requires separate evaluation.')\n"
    ))
    save_notebook(ROOT / "notebooks/reproduction_v10/reproduction.ipynb", reproduction)
    print(json.dumps({"generated": ["notebooks/submission/submission.ipynb", "notebooks/gpu_smoke/gpu_smoke.ipynb", "notebooks/reproduction_v10/reproduction.ipynb"]}))


if __name__ == "__main__":
    main()
