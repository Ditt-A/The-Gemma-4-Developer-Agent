"""Generate self-contained notebooks from agent/ and checked-in cell templates."""
import hashlib
import json
from pathlib import Path
import nbformat
from common import ROOT, read_agent_files, load_agent_config


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


def main():
    load_agent_config()
    members = {name: value.decode("utf-8") for name, value in read_agent_files().items()}
    code = nbformat.v4.new_code_cell
    markdown = nbformat.v4.new_markdown_cell
    package_cells = [
        markdown(source("templates/submission/intro.md")),
        code(source("templates/submission/setup.py")),
        code("# Generated from agent/; edit the source files and regenerate.\nFILES = " + repr(members) + "\nEXPECTED_MEMBER_HASHES = " + repr({name: hashlib.sha256(text.encode('utf-8')).hexdigest() for name, text in members.items()}) + "\n"),
        code(source("templates/submission/validate.py")),
        code(source("templates/submission/package.py")),
        markdown("Upload `/kaggle/working/submission.zip` through File Upload or `KaggleApi.competition_submit`. The packaging notebook does not run hidden evaluation. See docs/submission.md for authentication, validation and status checks."),
    ]
    save_notebook(ROOT / "notebooks/submission/submission.ipynb", package_cells)
    gpu_cells = [
        markdown("# Gemma 4 31B GPU compatibility check\n\nRun on Kaggle L4x4 with the organizer wheelhouse and model inputs. This checks serving and one tool call, not repair quality. The historical 300-second run expired during checkpoint loading. Choose a runtime that covers setup and model startup."),
        code("import time\nsmoke_started = time.perf_counter()"),
    ]
    gpu_cells += [code(cell.source) for cell in package_cells if cell.cell_type == "code"]
    gpu_cells += [code(source(f"templates/gpu_smoke/{name}.py")) for name in ("install", "serve", "check")]
    save_notebook(ROOT / "notebooks/gpu_smoke/gpu_smoke.ipynb", gpu_cells)
    print(json.dumps({"generated": ["notebooks/submission/submission.ipynb", "notebooks/gpu_smoke/gpu_smoke.ipynb"]}))


if __name__ == "__main__":
    main()
