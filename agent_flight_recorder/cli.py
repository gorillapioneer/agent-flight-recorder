"""
Simple Agent Flight Recorder CLI.

Public golden path:
    afr start "Fix auth bug"
    afr stop
    afr report
    afr handoff
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, OSError) as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout, result.stderr


def _require_repo(cwd: Path) -> Path:
    code, stdout, stderr = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if code != 0 or not stdout.strip():
        detail = stderr.strip() or "current directory is not inside a git repo"
        raise RuntimeError(detail)
    return Path(stdout.strip()).resolve()


def _git_text(args: list[str], repo: Path) -> str:
    code, stdout, _stderr = _run_git(args, repo)
    return stdout if code == 0 else ""


def _git_value(args: list[str], repo: Path, default: str = "unknown") -> str:
    value = _git_text(args, repo).strip()
    return value or default


def _slugify(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:48] or "mission"


def _afr_root(repo: Path) -> Path:
    return repo / ".afr"


def _sessions_root(repo: Path) -> Path:
    return _afr_root(repo) / "sessions"


def _current_path(repo: Path) -> Path:
    return _afr_root(repo) / "current.json"


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _session_path(repo: Path, session_ref: str) -> Path:
    session_dir = (repo / session_ref).resolve()
    sessions_root = _sessions_root(repo).resolve()
    if not _is_relative_to(session_dir, sessions_root):
        raise RuntimeError("Invalid AFR session path in .afr/current.json")
    return session_dir


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _display_path(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(path)


def _is_afr_path(path: str) -> bool:
    normalized = path.strip().strip('"').replace("\\", "/").rstrip("/")
    if " -> " in normalized:
        return any(_is_afr_path(part) for part in normalized.split(" -> ", 1))
    return normalized == ".afr" or normalized.startswith(".afr/")


def _parse_changed_files(status_text: str) -> list[str]:
    files: list[str] = []
    for line in status_text.splitlines():
        if not line.strip() or len(line) < 4:
            continue
        path = line[3:].strip().rstrip("/")
        if _is_afr_path(path):
            continue
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path and path not in files:
            files.append(path)
    return files


def _filter_recorder_status(status_text: str) -> str:
    lines = []
    for line in status_text.splitlines():
        path = line[3:].strip() if len(line) >= 4 else ""
        if _is_afr_path(path):
            continue
        lines.append(line)
    return "\n".join(lines) + ("\n" if lines else "")


def _git_diff(repo: Path) -> str:
    unstaged = _git_text(
        ["diff", "--no-ext-diff", "--", ".", ":(exclude).afr/**"],
        repo,
    ).rstrip()
    staged = _git_text(
        ["diff", "--cached", "--no-ext-diff", "--", ".", ":(exclude).afr/**"],
        repo,
    ).rstrip()
    parts = [
        "## Unstaged changes",
        unstaged or "(empty)",
        "",
        "## Staged changes",
        staged or "(empty)",
        "",
    ]
    return "\n".join(parts)


def _latest_session(repo: Path) -> Path | None:
    sessions_root = _sessions_root(repo)
    if not sessions_root.is_dir():
        return None
    sessions = [path for path in sessions_root.iterdir() if path.is_dir()]
    if not sessions:
        return None
    return sorted(sessions, key=lambda path: path.name)[-1]


def _active_session(repo: Path) -> dict | None:
    current = _current_path(repo)
    if not current.exists():
        return None
    data = _read_json(current)
    return data if data.get("active") else None


def _session_from_current_or_latest(repo: Path) -> Path:
    current = _current_path(repo)
    if current.exists():
        data = _read_json(current)
        session_dir = data.get("session_dir")
        if session_dir:
            path = _session_path(repo, session_dir)
            if path.is_dir():
                return path

    latest = _latest_session(repo)
    if latest is not None:
        return latest
    raise RuntimeError("No AFR sessions found. Run: afr start \"Mission text\"")


def _duration(started_at: str, ended_at: str) -> str:
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(ended_at)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return "unknown"
    seconds = max(0.0, (end - start).total_seconds())
    return f"{seconds:.1f}s"


def _fenced(text: str, language: str = "text") -> str:
    body = text.rstrip() if text.strip() else "(empty)"
    return f"```{language}\n{body}\n```"


def _read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _working_tree_label(changed_files: list[str]) -> str:
    return (
        f"changed ({len(changed_files)} file{'s' if len(changed_files) != 1 else ''})"
        if changed_files
        else "clean"
    )


def _files_block(changed_files: list[str]) -> str:
    return (
        "\n".join(f"- `{path}`" for path in changed_files)
        if changed_files
        else "- No changed files recorded."
    )


def _evidence_paths(repo: Path, session_dir: Path) -> dict[str, str]:
    return {
        "session_dir": _display_path(session_dir, repo),
        "report": _display_path(session_dir / "report.md", repo),
        "memory_capsule_md": _display_path(session_dir / "memory-capsule.md", repo),
        "memory_capsule_json": _display_path(session_dir / "memory-capsule.json", repo),
        "diff": _display_path(session_dir / "git-diff.patch", repo),
        "files_changed": _display_path(session_dir / "files-changed.txt", repo),
        "status_before": _display_path(session_dir / "git-status-before.txt", repo),
        "status_after": _display_path(session_dir / "git-status-after.txt", repo),
    }


def _render_memory_capsule_json(
    repo: Path,
    session_dir: Path,
    before: dict,
    after: dict,
    changed_files: list[str],
) -> dict:
    return {
        "schema_version": "0.2",
        "kind": "afr.memory_capsule",
        "session_id": after.get("session_id") or before.get("session_id") or session_dir.name,
        "mission": before.get("mission", ""),
        "outcome": _working_tree_label(changed_files),
        "duration": _duration(before.get("started_at", ""), after.get("ended_at", "")),
        "repo_path": str(repo),
        "started_at": before.get("started_at", ""),
        "ended_at": after.get("ended_at", ""),
        "branch_before": before.get("branch", "unknown"),
        "branch_after": after.get("branch", "unknown"),
        "head_before": before.get("head_sha", "unknown"),
        "head_after": after.get("head_sha", "unknown"),
        "changed_files": changed_files,
        "evidence_paths": _evidence_paths(repo, session_dir),
        "notes": {
            "important_decisions": [],
            "bugs_discovered": [],
            "commands_that_worked": [],
            "commands_that_failed": [],
            "useful_lesson_for_next_agent": "",
            "rollback_note": "Review git-diff.patch and revert the listed files if needed.",
        },
    }


def _render_memory_capsule_md(capsule: dict) -> str:
    files = capsule.get("changed_files", [])
    evidence = capsule.get("evidence_paths", {})
    files_block = _files_block(files)
    evidence_block = "\n".join(
        f"- {label}: `{path}`" for label, path in evidence.items()
    )
    return "\n".join([
        "# AFR Memory Capsule",
        "",
        "This is a compact, evidence-linked memory note for the next agent. Raw evidence remains the source of truth.",
        "",
        f"Mission: {capsule.get('mission', '')}",
        f"Outcome: {capsule.get('outcome', '')}",
        f"Duration: {capsule.get('duration', '')}",
        f"Repo: {capsule.get('repo_path', '')}",
        f"Branch: {capsule.get('branch_before', 'unknown')} -> {capsule.get('branch_after', 'unknown')}",
        f"HEAD: {capsule.get('head_before', 'unknown')} -> {capsule.get('head_after', 'unknown')}",
        "",
        "Files changed:",
        files_block,
        "",
        "Important decisions:",
        "- Not recorded automatically. Add human or agent notes here after review.",
        "",
        "Bugs discovered:",
        "- Not recorded automatically. Add confirmed bugs here after review.",
        "",
        "Commands that worked:",
        "- Not recorded automatically. Add known-good commands here after review.",
        "",
        "Commands that failed:",
        "- Not recorded automatically. Add failed commands here after review.",
        "",
        "Useful lesson for next agent:",
        "- Inspect the report and diff before continuing. Do not treat this capsule as a substitute for evidence.",
        "",
        "Rollback note:",
        "- Review `git-diff.patch` and revert the listed files if needed.",
        "",
        "Raw evidence:",
        evidence_block or "- No evidence paths recorded.",
        "",
    ])


def _write_memory_capsule(
    repo: Path,
    session_dir: Path,
    before: dict,
    after: dict,
    changed_files: list[str],
) -> dict:
    capsule = _render_memory_capsule_json(repo, session_dir, before, after, changed_files)
    _write_json(session_dir / "memory-capsule.json", capsule)
    _write_text(session_dir / "memory-capsule.md", _render_memory_capsule_md(capsule))
    return capsule


def _load_session_artifacts(repo: Path, session_dir: Path) -> tuple[dict, dict, list[str]]:
    before_path = session_dir / "before.json"
    after_path = session_dir / "after.json"
    if not before_path.exists() or not after_path.exists():
        raise RuntimeError("Session is incomplete. Run: afr stop")

    before = _read_json(before_path)
    after = _read_json(after_path)
    changed_files = after.get("changed_files")
    if not isinstance(changed_files, list):
        changed_files = _parse_changed_files(_read_text_if_exists(session_dir / "git-status-after.txt"))
    return before, after, [str(path) for path in changed_files]


def _render_handoff_prompt(
    repo: Path,
    session_dir: Path,
    before: dict,
    after: dict,
    changed_files: list[str],
) -> str:
    evidence = _evidence_paths(repo, session_dir)
    files_block = _files_block(changed_files)
    return "\n".join([
        "# AFR Agent Handoff",
        "",
        "You are continuing a coding mission recorded by Agent Flight Recorder.",
        "Treat the raw evidence as the source of truth. Do not assume the previous agent was correct.",
        "",
        f"Mission: {before.get('mission', '')}",
        f"Repo: {repo}",
        f"Session: {after.get('session_id') or before.get('session_id') or session_dir.name}",
        f"Duration: {_duration(before.get('started_at', ''), after.get('ended_at', ''))}",
        f"Branch: {before.get('branch', 'unknown')} -> {after.get('branch', 'unknown')}",
        f"HEAD: {before.get('head_sha', 'unknown')} -> {after.get('head_sha', 'unknown')}",
        f"Working tree: {_working_tree_label(changed_files)}",
        "",
        "Files changed:",
        files_block,
        "",
        "Tests run:",
        "- Not recorded automatically by AFR. Check the report, terminal logs, CI, or project notes.",
        "",
        "Known risks:",
        "- Review `git-diff.patch` before trusting the changes.",
        "- Re-run the relevant tests before continuing or merging.",
        "- Keep `.afr/` local and uncommitted unless intentionally scrubbed.",
        "",
        "Next recommended step:",
        "1. Read `report.md`.",
        "2. Inspect `git-diff.patch`.",
        "3. Continue from the changed files above.",
        "4. Add human notes to `memory-capsule.md` if anything important should be remembered.",
        "",
        "Raw evidence:",
        f"- Report: `{evidence['report']}`",
        f"- Memory capsule: `{evidence['memory_capsule_md']}`",
        f"- Diff: `{evidence['diff']}`",
        f"- Files changed: `{evidence['files_changed']}`",
        f"- Session directory: `{evidence['session_dir']}`",
        "",
    ])


def _render_report(
    repo: Path,
    session_dir: Path,
    before: dict,
    after: dict,
    status_before: str,
    status_after: str,
    diff_text: str,
    changed_files: list[str],
) -> str:
    working_tree = _working_tree_label(changed_files)
    files_block = _files_block(changed_files)

    return "\n".join([
        "# Agent Flight Recorder Report",
        "",
        "Raw evidence is the source of truth. Summaries are optional and should never replace the captured logs and diffs.",
        "",
        f"Mission: {before.get('mission', '')}",
        f"Duration: {_duration(before.get('started_at', ''), after.get('ended_at', ''))}",
        f"Repo: {repo}",
        f"Branch: {before.get('branch', 'unknown')} -> {after.get('branch', 'unknown')}",
        f"HEAD before: {before.get('head_sha', 'unknown')}",
        f"HEAD after: {after.get('head_sha', 'unknown')}",
        f"Working tree: {working_tree}",
        "",
        "Files changed:",
        files_block,
        "",
        "Git status before:",
        _fenced(status_before),
        "",
        "Git status after:",
        _fenced(status_after),
        "",
        f"Diff: `{_display_path(session_dir / 'git-diff.patch', repo)}`",
        _fenced(diff_text, "diff"),
        "",
        f"Raw evidence path: `{_display_path(session_dir, repo)}`",
        "",
    ])


def cmd_start(args: argparse.Namespace) -> int:
    repo = _require_repo(Path.cwd())
    if _active_session(repo):
        raise RuntimeError("An AFR recording is already active. Run: afr stop")

    mission = " ".join(args.mission).strip()
    started = _now()
    session_id = f"{started.strftime('%Y%m%d-%H%M%S')}-{_slugify(mission)}"
    session_dir = _sessions_root(repo) / session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    status_before = _filter_recorder_status(_git_text(["status", "--short"], repo))
    before = {
        "schema_version": "0.1",
        "session_id": session_id,
        "mission": mission,
        "started_at": started.isoformat(),
        "repo_path": str(repo),
        "branch": _git_value(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "head_sha": _git_value(["rev-parse", "HEAD"], repo),
    }

    _write_json(session_dir / "before.json", before)
    _write_text(session_dir / "git-status-before.txt", status_before)
    _write_json(_current_path(repo), {
        "active": True,
        "session_id": session_id,
        "session_dir": _display_path(session_dir, repo),
        "started_at": before["started_at"],
    })

    print("Recording started. Run your coding agent now. When done, run: afr stop")
    return 0


def cmd_stop(_args: argparse.Namespace) -> int:
    repo = _require_repo(Path.cwd())
    active = _active_session(repo)
    if not active:
        raise RuntimeError("No active AFR recording. Run: afr start \"Mission text\"")

    session_dir = _session_path(repo, active["session_dir"])
    before = _read_json(session_dir / "before.json")
    ended = _now()
    status_after = _filter_recorder_status(_git_text(["status", "--short"], repo))
    diff_text = _git_diff(repo)
    changed_files = _parse_changed_files(status_after)
    after = {
        "schema_version": "0.1",
        "session_id": before.get("session_id", session_dir.name),
        "mission": before.get("mission", ""),
        "started_at": before.get("started_at", ""),
        "ended_at": ended.isoformat(),
        "repo_path": str(repo),
        "branch": _git_value(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "head_sha": _git_value(["rev-parse", "HEAD"], repo),
        "changed_files": changed_files,
        "changed_files_count": len(changed_files),
    }
    status_before = (session_dir / "git-status-before.txt").read_text(
        encoding="utf-8"
    )

    _write_json(session_dir / "after.json", after)
    _write_text(session_dir / "git-status-after.txt", status_after)
    _write_text(session_dir / "git-diff.patch", diff_text)
    _write_text(session_dir / "files-changed.txt", "\n".join(changed_files) + ("\n" if changed_files else ""))
    report = _render_report(
        repo=repo,
        session_dir=session_dir,
        before=before,
        after=after,
        status_before=status_before,
        status_after=status_after,
        diff_text=diff_text,
        changed_files=changed_files,
    )
    report_path = session_dir / "report.md"
    _write_text(report_path, report)
    capsule = _write_memory_capsule(
        repo=repo,
        session_dir=session_dir,
        before=before,
        after=after,
        changed_files=changed_files,
    )
    _write_json(_current_path(repo), {
        "active": False,
        "session_id": after["session_id"],
        "session_dir": _display_path(session_dir, repo),
        "report_path": _display_path(report_path, repo),
        "memory_capsule_path": capsule["evidence_paths"]["memory_capsule_md"],
        "ended_at": after["ended_at"],
    })

    print(f"Report: {_display_path(report_path, repo)}")
    return 0


def cmd_report(_args: argparse.Namespace) -> int:
    repo = _require_repo(Path.cwd())
    session_dir = _session_from_current_or_latest(repo)
    report_path = session_dir / "report.md"
    if not report_path.exists():
        raise RuntimeError("No report found for the current session. Run: afr stop")

    print(report_path.read_text(encoding="utf-8"), end="")
    print(f"Report path: {_display_path(report_path, repo)}")
    return 0


def cmd_handoff(_args: argparse.Namespace) -> int:
    repo = _require_repo(Path.cwd())
    session_dir = _session_from_current_or_latest(repo)
    before, after, changed_files = _load_session_artifacts(repo, session_dir)

    capsule_path = session_dir / "memory-capsule.md"
    if not capsule_path.exists():
        _write_memory_capsule(repo, session_dir, before, after, changed_files)

    print(_render_handoff_prompt(repo, session_dir, before, after, changed_files), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="afr",
        description="Agent Flight Recorder: local-first black box recorder for AI coding agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start recording a mission.")
    start.add_argument("mission", nargs="+", help='Mission text, e.g. "Fix auth bug".')
    start.set_defaults(func=cmd_start)

    stop = sub.add_parser("stop", help="Stop the active recording and write report.md.")
    stop.set_defaults(func=cmd_stop)

    report = sub.add_parser("report", help="Print the current/latest report.")
    report.set_defaults(func=cmd_report)

    handoff = sub.add_parser("handoff", help="Print a copy-paste handoff prompt for the current/latest session.")
    handoff.set_defaults(func=cmd_handoff)

    return parser


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
