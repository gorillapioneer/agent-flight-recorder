"""Stdlib-only CLI for Agent Flight Recorder."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


RUNS_DIR = ".agent-runs"
MEMORY_DIR = ".agent-memory"
CURRENT_RUN_FILE = "current-run.txt"

RUN_FILES = {
    "flight-record.json": None,
    "mission.md": "# Mission\n\n",
    "plan.md": "# Plan\n\n",
    "commands.log": "",
    "diff.patch": "",
    "checks.json": "[]\n",
    "lessons.md": "# Lessons\n\n",
    "rollback.md": "# Rollback\n\n",
    "final-report.md": "# Final Report\n\n",
}

FIREWALL_RULES = [
    (
        "private key block",
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.IGNORECASE | re.DOTALL,
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
    (
        "connection string with credentials",
        re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s]+@[^\s]+", re.IGNORECASE),
        "[REDACTED_CONNECTION_STRING]",
    ),
    (
        "secret-like assignment",
        re.compile(
            r"(?im)^\s*[A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASS|API_KEY|BROKER_KEY)[A-Z0-9_]*\s*[:=]\s*.+$"
        ),
        "[REDACTED_SECRET_ASSIGNMENT]",
    ),
    (
        "inline credential assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|token|api_key|apikey|broker_key)\s*[:=]\s*[^\s,;]+"
        ),
        "[REDACTED_CREDENTIAL_ASSIGNMENT]",
    ),
    (
        "common key prefix",
        re.compile(
            r"\b(?:sk-|pk_live_|rk_live_|AKIA|AIza|ghp_|ghs_|glpat-|xox[baprs]-|ya29\.)[A-Za-z0-9._-]{8,}"
        ),
        "[REDACTED_KEY_PREFIX]",
    ),
    (
        "private data placeholder",
        re.compile(r"(?i)<(?:customer|client|private|personal)[^>]*>|\[(?:customer|client|private|personal)[^\]]*\]"),
        "[REDACTED_PRIVATE_DATA_PLACEHOLDER]",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_root() -> Path:
    return Path.cwd()


def runs_dir(root: Path) -> Path:
    return root / RUNS_DIR


def memory_dir(root: Path) -> Path:
    return root / MEMORY_DIR


def current_run_path(root: Path) -> Path:
    return runs_dir(root) / CURRENT_RUN_FILE


def run_dir(root: Path, run_id: str) -> Path:
    return runs_dir(root) / run_id


def ensure_workspace(root: Path) -> None:
    runs = runs_dir(root)
    memory = memory_dir(root)
    runs.mkdir(exist_ok=True)
    memory.mkdir(exist_ok=True)
    run_ignore = runs / ".gitignore"
    if not run_ignore.exists():
        run_ignore.write_text("*\n!.gitignore\n", encoding="utf-8")


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_paths(paths: list[str] | None) -> list[str]:
    return dedupe([(p or "").replace("\\", "/").strip() for p in (paths or []) if (p or "").strip()])


def make_run_id(agent: str) -> str:
    agent_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", agent.strip().lower()).strip("-") or "agent"
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{agent_slug}-{uuid.uuid4().hex[:8]}"


def default_record(args: argparse.Namespace, run_id: str) -> dict:
    return {
        "run_id": run_id,
        "mission": args.mission,
        "agent": args.agent,
        "started_at": utc_now(),
        "finished_at": None,
        "risk_level": args.risk_level,
        "allowed_files": normalize_paths(args.allowed_file),
        "blocked_files": normalize_paths(args.blocked_file),
        "planned_files": normalize_paths(args.planned_file),
        "actual_files_touched": [],
        "unexpected_files_touched": [],
        "commands_run": [],
        "checks": [],
        "diff_summary": "",
        "outcome": "",
        "rollback": "",
        "lessons": [],
        "human_approval_required": args.human_approval_required == "yes",
        "human_approval_status": "pending",
    }


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_record(root: Path, run_id: str) -> dict:
    path = run_dir(root, run_id) / "flight-record.json"
    if not path.exists():
        raise SystemExit(f"Run not found: {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_record(root: Path, record: dict) -> None:
    save_json(run_dir(root, record["run_id"]) / "flight-record.json", record)


def active_run_id(root: Path) -> str:
    path = current_run_path(root)
    if not path.exists():
        raise SystemExit("No active run. Pass --run-id or start a run first.")
    run_id = path.read_text(encoding="utf-8").strip()
    if not run_id:
        raise SystemExit("Active run file is empty. Pass --run-id or start a new run.")
    return run_id


def resolve_run_id(root: Path, run_id: str | None) -> str:
    return run_id or active_run_id(root)


def write_required_run_files(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False)
    for name, content in RUN_FILES.items():
        if content is not None:
            (path / name).write_text(content, encoding="utf-8")


def read_payload(args: argparse.Namespace) -> str:
    if getattr(args, "rollback", None) is not None:
        return args.rollback
    if getattr(args, "rollback_file", None):
        return Path(args.rollback_file).read_text(encoding="utf-8")
    if getattr(args, "text", None) is not None:
        return args.text
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    if getattr(args, "stdin", False):
        return sys.stdin.read()
    return ""


def append_section(path: Path, heading: str, body: str) -> None:
    body = body.rstrip()
    if not body:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {heading}\n\n{body}\n")


def parse_diff_files(diff_text: str) -> list[str]:
    files: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                candidate = parts[3]
                if candidate.startswith("b/"):
                    files.append(candidate[2:])
        elif line.startswith("+++ b/"):
            files.append(line[6:])
    return normalize_paths([f for f in files if f != "/dev/null"])


def update_touched_files(record: dict, touched: list[str]) -> None:
    actual = normalize_paths(record.get("actual_files_touched", []) + touched)
    expected = set(normalize_paths(record.get("allowed_files", []) + record.get("planned_files", [])))
    blocked = set(normalize_paths(record.get("blocked_files", [])))
    unexpected = []
    for path in actual:
        is_expected = path in expected or any(path.startswith(prefix.rstrip("/") + "/") for prefix in expected)
        is_blocked = path in blocked or any(path.startswith(prefix.rstrip("/") + "/") for prefix in blocked)
        if not is_expected or is_blocked:
            unexpected.append(path)
    record["actual_files_touched"] = actual
    record["unexpected_files_touched"] = normalize_paths(unexpected)


def run_git_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--no-ext-diff"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def apply_memory_firewall(text: str) -> tuple[str, list[str]]:
    redacted = text
    events: list[str] = []
    for name, pattern, replacement in FIREWALL_RULES:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            events.append(f"{name}: {count}")
    return redacted, events


def command_init(args: argparse.Namespace) -> int:
    root = repo_root()
    ensure_workspace(root)
    print(f"Initialized {RUNS_DIR}/ and {MEMORY_DIR}/")
    return 0


def command_start(args: argparse.Namespace) -> int:
    root = repo_root()
    ensure_workspace(root)
    run_id = args.run_id or make_run_id(args.agent)
    path = run_dir(root, run_id)
    write_required_run_files(path)
    record = default_record(args, run_id)
    save_record(root, record)
    (path / "mission.md").write_text(f"# Mission\n\n{args.mission}\n", encoding="utf-8")
    current_run_path(root).write_text(run_id + "\n", encoding="utf-8")
    print(f"Started run: {run_id}")
    print(f"Run directory: {path}")
    return 0


def command_add_plan(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    text = read_payload(args)
    if text:
        append_section(run_dir(root, run_id) / "plan.md", utc_now(), text)
    record["planned_files"] = normalize_paths(record.get("planned_files", []) + normalize_paths(args.planned_file))
    save_record(root, record)
    print(f"Updated plan for run: {run_id}")
    return 0


def command_capture_diff(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    if args.from_file:
        diff_text = Path(args.from_file).read_text(encoding="utf-8")
    else:
        diff_text = run_git_diff()
    (run_dir(root, run_id) / "diff.patch").write_text(diff_text, encoding="utf-8")
    update_touched_files(record, parse_diff_files(diff_text))
    if args.summary:
        record["diff_summary"] = args.summary
    save_record(root, record)
    print(f"Captured diff for run: {run_id}")
    print(f"Files touched: {len(record['actual_files_touched'])}")
    return 0


def command_add_command(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    entry = {
        "command": args.command,
        "cwd": args.cwd or str(root),
        "exit_code": args.exit_code,
        "recorded_at": utc_now(),
        "note": args.note or "",
    }
    record.setdefault("commands_run", []).append(entry)
    with (run_dir(root, run_id) / "commands.log").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    save_record(root, record)
    print(f"Recorded command for run: {run_id}")
    return 0


def command_add_check(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    entry = {
        "name": args.name,
        "status": args.status,
        "command": args.command or "",
        "summary": args.summary or "",
        "recorded_at": utc_now(),
    }
    record.setdefault("checks", []).append(entry)
    checks_path = run_dir(root, run_id) / "checks.json"
    save_json(checks_path, record["checks"])
    save_record(root, record)
    print(f"Recorded check for run: {run_id}")
    return 0


def command_add_lesson(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    text = read_payload(args).strip()
    if not text:
        raise SystemExit("Lesson text is required.")
    append_section(run_dir(root, run_id) / "lessons.md", utc_now(), text)
    record.setdefault("lessons", []).append(text)
    save_record(root, record)
    print(f"Recorded lesson for run: {run_id}")
    return 0


def command_finish(args: argparse.Namespace) -> int:
    root = repo_root()
    run_id = resolve_run_id(root, args.run_id)
    record = load_record(root, run_id)
    rollback = read_payload(args).strip() or "Rollback requires human review before deployment."
    record["finished_at"] = utc_now()
    record["outcome"] = args.outcome
    record["rollback"] = rollback
    record["human_approval_status"] = args.human_approval_status
    if args.diff_summary:
        record["diff_summary"] = args.diff_summary
    path = run_dir(root, run_id)
    path.joinpath("rollback.md").write_text(f"# Rollback\n\n{rollback}\n", encoding="utf-8")
    final = build_final_report(record)
    path.joinpath("final-report.md").write_text(final, encoding="utf-8")
    save_record(root, record)
    current = current_run_path(root)
    if current.exists() and current.read_text(encoding="utf-8").strip() == run_id:
        current.unlink()
    print(f"Finished run: {run_id}")
    print(f"Outcome: {args.outcome}")
    return 0


def build_final_report(record: dict) -> str:
    checks = record.get("checks", [])
    lessons = record.get("lessons", [])
    lines = [
        "# Final Report",
        "",
        f"Run ID: {record['run_id']}",
        f"Mission: {record.get('mission', '')}",
        f"Agent: {record.get('agent', '')}",
        f"Risk level: {record.get('risk_level', '')}",
        f"Outcome: {record.get('outcome', '')}",
        f"Human approval required: {record.get('human_approval_required', True)}",
        f"Human approval status: {record.get('human_approval_status', '')}",
        "",
        "## Files",
        "",
        f"Planned: {', '.join(record.get('planned_files', [])) or 'none recorded'}",
        f"Actual: {', '.join(record.get('actual_files_touched', [])) or 'none recorded'}",
        f"Unexpected: {', '.join(record.get('unexpected_files_touched', [])) or 'none'}",
        "",
        "## Checks",
        "",
    ]
    if checks:
        for check in checks:
            lines.append(f"- {check['name']}: {check['status']} - {check.get('summary', '')}")
    else:
        lines.append("- none recorded")
    lines.extend(["", "## Diff Summary", "", record.get("diff_summary", "") or "No summary recorded."])
    lines.extend(["", "## Rollback", "", record.get("rollback", "") or "No rollback recorded."])
    lines.extend(["", "## Lessons", ""])
    if lessons:
        lines.extend([f"- {lesson}" for lesson in lessons])
    else:
        lines.append("- none recorded")
    return "\n".join(lines).rstrip() + "\n"


def command_build_memory(args: argparse.Namespace) -> int:
    root = repo_root()
    ensure_workspace(root)
    sections = [
        "# Project Memory",
        "",
        "Generated by Agent Flight Recorder from successful runs.",
        "Review this file before committing it to a public repository.",
        "",
    ]
    count = 0
    for record_path in sorted(runs_dir(root).glob("*/flight-record.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("outcome") != "success" and not args.include_non_success:
            continue
        count += 1
        sections.extend(memory_section(record))
    if count == 0:
        sections.extend(["## No Successful Runs Yet", "", "Finish a run with `--outcome success`, then rebuild memory.", ""])
    memory_text = "\n".join(sections).rstrip() + "\n"
    memory_text, events = apply_memory_firewall(memory_text)
    if events:
        memory_text += "\n## Memory Firewall Notes\n\n"
        for event in events:
            memory_text += f"- Redacted {event}\n"
    memory_path = memory_dir(root) / "PROJECT_MEMORY.md"
    memory_path.write_text(memory_text, encoding="utf-8")
    print(f"Built memory: {memory_path}")
    print(f"Runs included: {count}")
    if events:
        print(f"Memory firewall redactions: {len(events)}")
    return 0


def memory_section(record: dict) -> list[str]:
    lines = [
        f"## {record.get('mission', 'Untitled mission')}",
        "",
        f"- Run ID: `{record.get('run_id', '')}`",
        f"- Agent: {record.get('agent', '')}",
        f"- Risk level: {record.get('risk_level', '')}",
        f"- Outcome: {record.get('outcome', '')}",
        f"- Files touched: {', '.join(record.get('actual_files_touched', [])) or 'none recorded'}",
        f"- Unexpected files: {', '.join(record.get('unexpected_files_touched', [])) or 'none'}",
        f"- Diff summary: {record.get('diff_summary', '') or 'none recorded'}",
        "",
        "### Checks",
        "",
    ]
    checks = record.get("checks", [])
    if checks:
        lines.extend([f"- {check.get('name', '')}: {check.get('status', '')} - {check.get('summary', '')}" for check in checks])
    else:
        lines.append("- none recorded")
    lines.extend(["", "### Lessons", ""])
    lessons = record.get("lessons", [])
    if lessons:
        lines.extend([f"- {lesson}" for lesson in lessons])
    else:
        lines.append("- none recorded")
    lines.extend(["", "### Rollback", "", record.get("rollback", "") or "No rollback recorded.", ""])
    return lines


def add_text_args(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="Text to add.")
    source.add_argument("--file", help="Read text from a file.")
    source.add_argument("--stdin", action="store_true", help="Read text from stdin.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-flight-recorder",
        description="Black-box telemetry and project memory for AI coding agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="Create .agent-runs/ and .agent-memory/.")
    init_parser.set_defaults(func=command_init)

    start = sub.add_parser("start", help="Start a new flight record.")
    start.add_argument("--mission", required=True)
    start.add_argument("--agent", default="unspecified-agent")
    start.add_argument("--risk-level", choices=["GREEN", "AMBER", "RED", "BLACK"], default="AMBER")
    start.add_argument("--allowed-file", action="append")
    start.add_argument("--blocked-file", action="append")
    start.add_argument("--planned-file", action="append")
    start.add_argument("--run-id")
    start.add_argument("--human-approval-required", choices=["yes", "no"], default="yes")
    start.set_defaults(func=command_start)

    add_plan = sub.add_parser("add-plan", help="Add plan text and planned files.")
    add_plan.add_argument("--run-id")
    add_plan.add_argument("--planned-file", action="append")
    add_text_args(add_plan)
    add_plan.set_defaults(func=command_add_plan)

    diff = sub.add_parser("capture-diff", help="Capture git diff or a patch file.")
    diff.add_argument("--run-id")
    diff.add_argument("--from-file")
    diff.add_argument("--summary")
    diff.set_defaults(func=command_capture_diff)

    command = sub.add_parser("add-command", help="Record a command that was run elsewhere.")
    command.add_argument("--run-id")
    command.add_argument("--command", required=True)
    command.add_argument("--exit-code", type=int, default=0)
    command.add_argument("--cwd")
    command.add_argument("--note")
    command.set_defaults(func=command_add_command)

    check = sub.add_parser("add-check", help="Record a safety check or test result.")
    check.add_argument("--run-id")
    check.add_argument("--name", required=True)
    check.add_argument("--status", choices=["pass", "warn", "fail", "skip"], required=True)
    check.add_argument("--command")
    check.add_argument("--summary")
    check.set_defaults(func=command_add_check)

    lesson = sub.add_parser("add-lesson", help="Record a lesson for memory.")
    lesson.add_argument("--run-id")
    add_text_args(lesson)
    lesson.set_defaults(func=command_add_lesson)

    finish = sub.add_parser("finish", help="Finish a run and write final-report.md.")
    finish.add_argument("--run-id")
    finish.add_argument("--outcome", choices=["success", "partial", "failed", "cancelled"], required=True)
    finish.add_argument("--diff-summary")
    finish.add_argument("--human-approval-status", choices=["pending", "approved", "rejected", "not_required"], default="pending")
    rollback_source = finish.add_mutually_exclusive_group()
    rollback_source.add_argument("--rollback", help="Rollback plan text.")
    rollback_source.add_argument("--rollback-file", help="Read rollback plan from a file.")
    rollback_source.add_argument("--stdin", action="store_true", help="Read rollback plan from stdin.")
    finish.set_defaults(func=command_finish)

    memory = sub.add_parser("build-memory", help="Build .agent-memory/PROJECT_MEMORY.md from successful runs.")
    memory.add_argument("--include-non-success", action="store_true", help="Include partial, failed, or cancelled runs.")
    memory.set_defaults(func=command_build_memory)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
