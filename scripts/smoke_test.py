"""CLI smoke test for the Agent Flight Recorder v0.1 golden path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)
    return output


def run_cli(project: Path, *args: str) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return run([sys.executable, "-m", "agent_flight_recorder", *args], project, env=env)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="afr-smoke-") as tmp:
        project = Path(tmp)

        run(["git", "init"], project)
        run(["git", "config", "user.email", "afr-smoke@example.com"], project)
        run(["git", "config", "user.name", "AFR Smoke"], project)

        readme = project / "README.md"
        readme.write_text("hello\n", encoding="utf-8")
        run(["git", "add", "README.md"], project)
        run(["git", "commit", "-m", "initial"], project)

        start_output = run_cli(project, "start", "Smoke test simple recorder")
        assert "Recording started" in start_output

        readme.write_text("changed\n", encoding="utf-8")
        run(["git", "add", "README.md"], project)
        (project / "notes.txt").write_text("extra\n", encoding="utf-8")

        stop_output = run_cli(project, "stop")
        assert "Report: .afr/sessions/" in stop_output

        report_output = run_cli(project, "report")
        assert "# Agent Flight Recorder Report" in report_output
        assert "Mission: Smoke test simple recorder" in report_output
        assert "README.md" in report_output
        assert "notes.txt" in report_output

        afr_root = project / ".afr"
        current = json.loads((afr_root / "current.json").read_text(encoding="utf-8"))
        assert current["active"] is False

        sessions = list((afr_root / "sessions").iterdir())
        assert len(sessions) == 1
        session = sessions[0]
        required = [
            "before.json",
            "after.json",
            "git-status-before.txt",
            "git-status-after.txt",
            "git-diff.patch",
            "files-changed.txt",
            "report.md",
        ]
        missing = [name for name in required if not (session / name).exists()]
        if missing:
            raise AssertionError(f"Missing AFR session files: {missing}")

        changed_files = (session / "files-changed.txt").read_text(encoding="utf-8")
        assert "README.md" in changed_files
        assert "notes.txt" in changed_files
        assert ".afr" not in changed_files

        patch = (session / "git-diff.patch").read_text(encoding="utf-8")
        assert "## Unstaged changes" in patch
        assert "## Staged changes" in patch
        assert "README.md" in patch
        assert ".afr" not in patch

    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
