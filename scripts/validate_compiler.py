"""Run the official compiler and an ADK tool-flow fixture, without an external model."""
import asyncio
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from common import ROOT, AGENT_DIR, RUNS, build_bundle, load_agent_config, sha256_file, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    os.environ["OTEL_SDK_DISABLED"] = "true"
    bundle, _ = build_bundle()
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="compiler_fixture_", dir=local) as temporary:
        from adk_submission import compile_submission, ModelRegistry, SubmissionLimits, GenerationConstraints, NumericRange, validate_directory
        from google.adk.models.base_llm import BaseLlm
        from google.adk.models.llm_response import LlmResponse
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from pydantic import PrivateAttr

        fixture = Path(temporary)
        fixture.mkdir(parents=True, exist_ok=True)
        assert fixture.resolve().is_relative_to(ROOT.resolve())
        (fixture / "calculator.py").write_text("def clamp(value):\n    return value\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=fixture, check=True)
        subprocess.run(["git", "add", "calculator.py"], cwd=fixture, check=True)
        if subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=fixture, capture_output=True).returncode != 0:
            subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost", "commit", "-qm", "baseline"], cwd=fixture, check=True)
        calls = []

        def path_for(name):
            result = (fixture / name).resolve()
            if not result.is_relative_to(fixture.resolve()):
                raise ValueError("Fixture path escape")
            return result

        def read_file(filepath: str, start_line: int | None = None, end_line: int | None = None) -> dict:
            calls.append("read_file")
            return {"status": "ok", "content": path_for(filepath).read_text(encoding="utf-8")}

        def edit_file(filepath: str, old_string: str, new_string: str, allow_multiple: bool = False) -> dict:
            calls.append("edit_file")
            path = path_for(filepath)
            source = path.read_text(encoding="utf-8")
            assert source.count(old_string) == 1
            path.write_text(source.replace(old_string, new_string), encoding="utf-8")
            return {"status": "ok"}

        def write_file(filepath: str, content: str) -> dict:
            path_for(filepath).write_text(content, encoding="utf-8")
            return {"status": "ok"}

        def run_command(command: str) -> dict:
            calls.append("run_command")
            # This scripted fixture has a single predefined check and never executes model-supplied shell.
            assert command == "check clamp"
            result = subprocess.run([sys.executable, "-c", "from calculator import clamp; assert clamp(-3)==0; assert clamp(2)==2"], cwd=fixture, capture_output=True, text=True)
            return {"status": "ok", "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}

        def get_status() -> dict:
            calls.append("get_status")
            return {"status": "ok", "tool_calls_used": len(calls), "time_seconds_remaining": 300}

        def submit_patch() -> dict:
            calls.append("submit_patch")
            patch = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=fixture, text=True)
            assert "return max(0, value)" in patch
            return {"status": "ok", "patch_size": len(patch), "files_changed": 1}

        def get_code_neighbors(node: str, edge_type: str | None = None, max_neighbors: int = 50) -> dict:
            return {"status": "ok", "neighbors": []}

        def search_similar_code(query: str, k: int = 10) -> dict:
            return {"status": "ok", "results": []}

        def get_code_subgraph(nodes: list[str]) -> dict:
            return {"status": "ok", "nodes": []}

        class ScriptedModel(BaseLlm):
            _step: int = PrivateAttr(default=0)

            async def generate_content_async(self, llm_request, stream=False):
                steps = [
                    ("read_file", {"filepath": "calculator.py", "start_line": 1, "end_line": 2}),
                    ("edit_file", {"filepath": "calculator.py", "old_string": "return value", "new_string": "return max(0, value)"}),
                    ("get_status", {}),
                    ("run_command", {"command": "check clamp"}),
                    ("submit_patch", {}),
                ]
                if self._step < len(steps):
                    name, arguments = steps[self._step]
                    part = types.Part(function_call=types.FunctionCall(name=name, args=arguments))
                else:
                    part = types.Part(text="Done.")
                self._step += 1
                yield LlmResponse(content=types.Content(role="model", parts=[part]))

        tools = {f.__name__: f for f in [run_command, read_file, edit_file, write_file, get_status, submit_patch, get_code_neighbors, search_similar_code, get_code_subgraph]}
        models = ModelRegistry()
        models.register(load_agent_config()["model"], ScriptedModel(model="fixture-only-not-gemma"))
        limits = SubmissionLimits(max_total_size_bytes=3 * 1024**3,
            allowed_file_extensions=frozenset({".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}),
            max_instruction_chars=1_000_000, max_total_instruction_chars=10_000_000)
        constraints = GenerationConstraints(allowed_fields=None, max_output_tokens=NumericRange(1, 32768), thinking_budget=NumericRange(0, 32768))
        agent_dir = AGENT_DIR
        config = load_agent_config()
        validate_directory(agent_dir, limits=limits)
        agent = compile_submission(agent_dir, tool_registry=tools, model_registry=models,
            limits=limits, generation_constraints=constraints)
        assert agent.generate_content_config.max_output_tokens == config["generate_content_config"]["max_output_tokens"]
        assert agent.generate_content_config.thinking_config.thinking_budget == config["generate_content_config"]["thinking_config"]["thinking_budget"]
        assert len(agent.tools) == 9 and len(agent.sub_agents) == 0

        async def exercise():
            sessions = InMemorySessionService()
            await sessions.create_session(app_name="candidate_fixture", user_id="fixture", session_id="smoke")
            runner = Runner(app_name="candidate_fixture", agent=agent, session_service=sessions)
            events = []
            async for event in runner.run_async(user_id="fixture", session_id="smoke", new_message=types.Content(role="user", parts=[types.Part(text="Fix clamp: negative values return zero and positive values remain unchanged.")])):
                events.append(event)
            return events

        events = asyncio.run(exercise())
        assert calls == ["read_file", "edit_file", "get_status", "run_command", "submit_patch"], calls
        result = subprocess.run([sys.executable, "-c", "from calculator import clamp; assert clamp(-5)==0; assert clamp(0)==0; assert clamp(7)==7"], cwd=fixture, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        receipt = {"notebook_cells_executed": False, "official_directory_validation": True,
            "official_compiler": "adk-submission 0.2.13 / google-adk 1.36.1",
            "compiled_single_agent": True, "compiled_tools": sorted(tools), "scripted_adk_integration": True,
            "native_tool_sequence": calls, "events": len(events),
            "fixture_behavioral_assertions": True, "quality_benchmark": False,
            "archive_sha256": sha256_file(bundle)}
        write_json(RUNS / "validation/compiler.json", receipt)
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
