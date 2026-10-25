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
from common import AGENT_DIR, CANDIDATE_ID, build_bundle, load_agent_config, submission_state, validate_archive
from reproduce_public import MANIFEST, UPSTREAM_DIR, verify_reference


class ProjectRegressionTests(unittest.TestCase):
    def test_current_combined_candidate_matches_its_manifest(self):
        manifest = json.loads((ROOT / "provenance/combined_v2.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            archive, receipt = build_bundle(output_dir=folder)
            self.assertEqual(receipt["candidate"], CANDIDATE_ID)
            self.assertEqual(receipt["archive_sha256"], manifest["archive_sha256"])
            self.assertEqual(archive.stat().st_size, manifest["archive_bytes"])

    def test_all_three_changes_are_combined_without_changing_other_budgets(self):
        current = load_agent_config()
        upstream = load_agent_config(UPSTREAM_DIR)
        expected_generation = dict(upstream["generate_content_config"], temperature=0)
        self.assertEqual(current["generate_content_config"], expected_generation)
        self.assertEqual(current["model"], upstream["model"])
        self.assertEqual(current["tools"], ["run_command", "read_file", "edit_file", "write_file", "get_status", "submit_patch"])
        self.assertEqual((AGENT_DIR / "eval_config.yaml").read_bytes(), (UPSTREAM_DIR / "eval_config.yaml").read_bytes())
        self.assertIn("# TOOL ERROR RECOVERY", current["instruction"])
        self.assertIn("After two failures trying the same operation, switch to a simpler alternative.", current["instruction"])
        for removed in ("search_similar_code", "get_code_neighbors", "get_code_subgraph"):
            self.assertNotIn(removed, current["instruction"])

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
                manifest = json.loads((ROOT / "provenance/combined_v2.json").read_text(encoding="utf-8"))
                self.assertEqual(receipt["archive_sha256"], manifest["archive_sha256"])
                self.assertEqual(scope["receipt"]["candidate"], CANDIDATE_ID)
            finally:
                os.chdir(original_cwd)

    def test_stale_or_extra_zip_members_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            archive, _ = build_bundle(output_dir=folder)
            with zipfile.ZipFile(archive, "a") as z:
                z.writestr("unexpected.txt", "not part of the agent")
            with self.assertRaisesRegex(ValueError, "Archive members"):
                validate_archive(archive)

    def test_public_v10_build_matches_the_scored_artifact(self):
        manifest = verify_reference()
        with tempfile.TemporaryDirectory() as folder:
            archive, receipt = build_bundle(UPSTREAM_DIR, folder, candidate_id=manifest["candidate_id"])
            self.assertEqual(receipt["archive_sha256"], manifest["archive_sha256"])
            self.assertEqual(archive.stat().st_size, manifest["archive_bytes"])
            self.assertEqual(receipt["members"], manifest["members"])
            self.assertEqual(receipt["candidate"], manifest["candidate_id"])

    def test_reproduction_notebook_outputs_the_exact_public_zip(self):
        import nbformat
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        notebook = nbformat.read(ROOT / "notebooks/reproduction_v10/reproduction.ipynb", as_version=4)
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
                            exec(compile(cell.source, "reproduction notebook", "exec"), scope)
                receipt = json.loads((scope["OUTPUT"] / "build_receipt.json").read_text(encoding="utf-8"))
                self.assertEqual(receipt["archive_sha256"], manifest["archive_sha256"])
                self.assertEqual(receipt["members"], manifest["members"])
                self.assertTrue(receipt["exact_public_artifact_reproduced"])
            finally:
                os.chdir(original_cwd)

    def test_wrong_expected_hash_stops_submission_before_authentication(self):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("KAGGLE_")}
        with tempfile.TemporaryDirectory() as folder:
            archive, _ = build_bundle(output_dir=folder)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/submit.py"), "--archive", str(archive),
                "--expected-sha256", "0" * 64, "--dry-run"], cwd=folder, env=environment,
                capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match --expected-sha256", result.stderr)

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
