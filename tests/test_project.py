"""Regression checks for the move from one-off scripts to a portable repository."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import AGENT_DIR, build_bundle, submission_state, validate_archive


class ProjectRegressionTests(unittest.TestCase):
    def test_original_submission_bytes_are_preserved(self):
        historical = json.loads((ROOT / "provenance/submitted_v1.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            archive, receipt = build_bundle(output_dir=folder)
            self.assertEqual(receipt["archive_sha256"], historical["submitted_archive_sha256"])
            self.assertEqual(archive.stat().st_size, historical["submitted_archive_bytes"])

    def test_packaging_works_outside_the_repository_cwd(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/build.py"), "--output-dir", folder],
                cwd=folder, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(Path(folder, "submission.zip").exists())

    def test_generated_notebook_rebuilds_the_same_archive(self):
        import nbformat
        notebook = nbformat.read(ROOT / "notebooks/submission/submission.ipynb", as_version=4)
        nbformat.validate(notebook)
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            scope = {"__name__": "__main__"}
            try:
                os.chdir(folder)
                with contextlib.redirect_stdout(io.StringIO()):
                    for cell in notebook.cells:
                        if cell.cell_type == "code":
                            self.assertEqual(cell.outputs, [])
                            exec(compile(cell.source, "generated notebook", "exec"), scope)
                receipt = validate_archive(scope["archive_path"])
                historical = json.loads((ROOT / "provenance/submitted_v1.json").read_text(encoding="utf-8"))
                self.assertEqual(receipt["archive_sha256"], historical["submitted_archive_sha256"])
            finally:
                os.chdir(original_cwd)

    def test_stale_or_extra_zip_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            archive, _ = build_bundle(output_dir=folder)
            with zipfile.ZipFile(archive, "a") as z:
                z.writestr("unexpected.txt", "not part of the agent")
            with self.assertRaisesRegex(ValueError, "Archive members"):
                validate_archive(archive)

    def test_error_takes_precedence_over_complete(self):
        self.assertEqual(submission_state({"status": "COMPLETE", "errorDescription": "rerun exception"}), "FAILED")

    def test_zero_is_a_real_score_and_missing_score_stays_pending(self):
        self.assertEqual(submission_state({"status": "COMPLETE", "publicScore": "0.00"}), "SCORED")
        self.assertEqual(submission_state({"status": "COMPLETE", "publicScore": ""}), "SUBMITTED_AWAITING_RESULT")

    def test_help_commands_do_not_require_credentials(self):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("KAGGLE_")}
        with tempfile.TemporaryDirectory() as folder:
            for script in ("notebooks.py", "submit.py", "status.py"):
                result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--help"], cwd=folder,
                    env=environment, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
