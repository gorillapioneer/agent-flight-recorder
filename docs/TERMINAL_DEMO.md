# Terminal Demo

Copy-pasteable example of what a user sees when running `afr`.

---

## 1. Install

```bash
pip install -e .
```

## 2. Start a session

```bash
afr start "Fix auth bug"
```

```
Recording started. Run your coding agent now. When done, run: afr stop
```

## 3. Run your agent

```bash
# run Claude Code, Aider, Cursor, Codex, or make changes manually
```

## 4. Stop the session

```bash
afr stop
```

```
Report: .afr/sessions/20260507-174301-fix-auth-bug/report.md
```

## 5. View the report

```bash
afr report
```

```
# Agent Flight Recorder Report

Raw evidence is the source of truth. Summaries are optional and should never replace the captured logs and diffs.

Mission: Fix auth bug
Duration: 42.8s
Branch: main -> fix-auth-bug
HEAD before: 4f7c2a9
HEAD after:  8a3d51e
Working tree: changed (3 files)

Files changed:
- src/auth/session.py
- tests/test_auth_session.py
- docs/auth-notes.md

Diff: .afr/sessions/20260507-174301-fix-auth-bug/git-diff.patch
Raw evidence path: .afr/sessions/20260507-174301-fix-auth-bug
```

---

Report path is printed so you can open, share, or paste it directly.
