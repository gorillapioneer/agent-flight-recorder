"""CLI smoke test for Agent Flight Recorder."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "smoke-run-001"


def run_cli(project: Path, *args: str) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "agent_flight_recorder", *args],
        cwd=project,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)
    return output


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="afr-smoke-") as tmp:
        project = Path(tmp)
        patch = project / "demo.patch"
        patch.write_text(
            "\n".join(
                [
                    "diff --git a/dashboard.txt b/dashboard.txt",
                    "--- a/dashboard.txt",
                    "+++ b/dashboard.txt",
                    "@@ -1 +1,2 @@",
                    " Dashboard",
                    "+API health badge: SAFE_PLACEHOLDER_STATUS",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        run_cli(project, "init")
        run_cli(
            project,
            "start",
            "--run-id",
            RUN_ID,
            "--mission",
            "Add an API health badge to a dashboard.",
            "--agent",
            "smoke-agent",
            "--risk-level",
            "AMBER",
            "--allowed-file",
            "dashboard.txt",
            "--planned-file",
            "dashboard.txt",
        )
        run_cli(
            project,
            "add-plan",
            "--text",
            "Add one badge, keep the change scoped, and leave review to a human.",
            "--planned-file",
            "dashboard.txt",
        )
        run_cli(
            project,
            "capture-diff",
            "--from-file",
            str(patch),
            "--summary",
            "Adds a safe placeholder status badge line to the dashboard.",
        )
        run_cli(
            project,
            "add-command",
            "--command",
            "python -m unittest",
            "--exit-code",
            "0",
            "--note",
            "Recorded smoke-test command, not executed by the recorder.",
        )
        run_cli(
            project,
            "add-check",
            "--name",
            "smoke-check",
            "--status",
            "pass",
            "--command",
            "python -m unittest",
            "--summary",
            "Smoke check passed.",
        )
        run_cli(
            project,
            "add-lesson",
            "--text",
            "Keep dashboard status changes small and avoid <customer-placeholder> in reusable memory.",
        )
        run_cli(
            project,
            "finish",
            "--outcome",
            "success",
            "--human-approval-status",
            "approved",
            "--diff-summary",
            "Small dashboard badge change.",
            "--rollback",
            "Revert the dashboard badge change if the UI status is confusing.",
        )
        run_cli(project, "build-memory")

        run_dir = project / ".agent-runs" / RUN_ID
        required = [
            "flight-record.json",
            "mission.md",
            "plan.md",
            "commands.log",
            "diff.patch",
            "checks.json",
            "lessons.md",
            "rollback.md",
            "final-report.md",
        ]
        missing = [name for name in required if not (run_dir / name).exists()]
        if missing:
            raise AssertionError(f"Missing run files: {missing}")

        record = json.loads((run_dir / "flight-record.json").read_text(encoding="utf-8"))
        assert record["outcome"] == "success"
        assert record["actual_files_touched"] == ["dashboard.txt"]
        assert record["unexpected_files_touched"] == []
        memory = (project / ".agent-memory" / "PROJECT_MEMORY.md").read_text(encoding="utf-8")
        assert "Add an API health badge" in memory
        assert "SAFE_PLACEHOLDER_STATUS" not in memory
        assert "<customer-placeholder>" not in memory
        assert "[REDACTED_PRIVATE_DATA_PLACEHOLDER]" in memory

    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
