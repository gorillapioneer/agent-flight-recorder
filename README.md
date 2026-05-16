# Agent Flight Recorder (`afr`)

AI agents are flying blind. This is their flight recorder.

Capture everything your coding agent changes before you lose it to scrollback.

```bash
afr start "Fix auth bug"
# run Claude Code, Codex, Aider, Cursor, OpenHands...
afr stop
afr report
afr handoff
```

Agent Flight Recorder is a local-first black box recorder for AI coding agents. It captures git state before and after a mission, changed files, diffs, and a clean Markdown report.

## Why

AI coding agents can move faster than your terminal scrollback. AFR gives each coding session a simple evidence trail:

- What the mission was
- Which repo, branch, and commit it started from
- Which branch and commit it ended on
- What the working tree looked like before and after
- Which files changed
- The raw git diff
- A Markdown report you can paste into an issue, pull request, or handoff note
- A memory capsule for compact, evidence-linked recall
- A handoff prompt for continuing work in another agent

Raw evidence is the source of truth. Summaries are optional and should never replace the captured logs and diffs.

## Install

```bash
pip install -e .
```

During development, you can also run the CLI module directly:

```bash
python -m agent_flight_recorder.cli --help
```

## Quickstart

Run these commands from inside a git repository:

```bash
afr start "Fix auth bug"
# run your coding agent or make manual changes
afr stop
afr report
afr handoff
```

`afr start` creates a local session and captures the initial git state.

`afr stop` captures the final git state, changed files, diff, writes `report.md`, and also writes `memory-capsule.md/json`.

`afr report` prints the latest/current report to stdout and prints the report path.

`afr handoff` prints a copy-paste prompt for handing the latest/current session to ChatGPT, Codex, Claude Code, Devin, or another coding agent.

## What it looks like

```
$ afr start "Fix auth bug"
Recording started. Run your coding agent now. When done, run: afr stop

$ afr stop
Report: .afr/sessions/20260507-174301-fix-auth-bug/report.md

$ afr report
Mission: Fix auth bug
Duration: 42.8s
Branch: main -> fix-auth-bug
HEAD before: 4f7c2a9
HEAD after:  8a3d51e
Working tree: changed (3 files)
Files changed: src/auth/session.py, tests/test_auth_session.py, docs/auth-notes.md
Diff: .afr/sessions/20260507-174301-fix-auth-bug/git-diff.patch
Raw evidence path: .afr/sessions/20260507-174301-fix-auth-bug

$ afr handoff
# AFR Agent Handoff
Mission: Fix auth bug
Files changed:
- `src/auth/session.py`
- `tests/test_auth_session.py`
Raw evidence:
- Report: `.afr/sessions/20260507-174301-fix-auth-bug/report.md`
- Memory capsule: `.afr/sessions/20260507-174301-fix-auth-bug/memory-capsule.md`
- Diff: `.afr/sessions/20260507-174301-fix-auth-bug/git-diff.patch`
```

Full annotated example: [`docs/TERMINAL_DEMO.md`](docs/TERMINAL_DEMO.md)

## Commands

### `afr start "Mission text"`

Starts a recording session.

It checks that the current directory is inside a git repo, creates a session under `.afr/sessions/`, captures branch and HEAD SHA, saves `git status --short`, and writes `.afr/current.json`.

### `afr stop`

Stops the active recording session.

It captures final branch and HEAD SHA, saves `git status --short`, writes `git diff` to a patch file, records changed files, generates `report.md`, writes `memory-capsule.md/json`, and marks the current session as closed.

### `afr report`

Prints the current or latest session report to stdout.

Use this when you want to paste the mission report into a pull request, issue, chat, or release note.

### `afr handoff`

Prints a copy-paste continuation prompt for the current or latest session.

Use this when moving work between agents or chats. The prompt points at the report, memory capsule, diff, changed-file list, and session directory.

## Storage

AFR writes local runtime evidence under `.afr/`:

```text
.afr/
  current.json
  sessions/
    <timestamp-slug>/
      before.json
      after.json
      git-status-before.txt
      git-status-after.txt
      git-diff.patch
      files-changed.txt
      report.md
      memory-capsule.md
      memory-capsule.json
```

`.afr/` is intended to stay local and should be gitignored. It can contain file paths, diffs, and other sensitive project context.

## Report Format

Reports are plain Markdown and start with:

```markdown
# Agent Flight Recorder Report

Raw evidence is the source of truth. Summaries are optional and should never replace the captured logs and diffs.

Mission:
Duration:
Repo:
Branch:
HEAD before:
HEAD after:
Working tree:
Files changed:
Git status before:
Git status after:
Diff:
Raw evidence path:
```

## Memory Capsule and Handoff

Each completed session also writes a compact memory capsule:

```text
memory-capsule.md
memory-capsule.json
```

The capsule records mission, outcome, duration, branch/HEAD movement, changed files, evidence paths, and empty note slots for decisions, bugs, working commands, failed commands, and lessons.

`afr handoff` turns the latest/current session into a continuation prompt for another agent. It does not invent a summary. It points the next agent back to the evidence.

## Example Report

See [`examples/sample-report.md`](examples/sample-report.md) for a concise public sample generated from a `Fix auth bug` mission.

## Demo and Launch Notes

- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) - simple 30-60 second demo flow.
- [`docs/LAUNCH_CHECKLIST.md`](docs/LAUNCH_CHECKLIST.md) - checklist before sharing the repo publicly.
- [`docs/AGENT_HANDOFF.md`](docs/AGENT_HANDOFF.md) - memory capsule and handoff workflow.

## Launch Materials

- [`docs/LAUNCH_POSTS.md`](docs/LAUNCH_POSTS.md) - post drafts, taglines, and video captions.
- [`docs/RECORDING_PLAN.md`](docs/RECORDING_PLAN.md) - 30-second recording plan with commands, overlays, and voiceover.

## Agent Compatibility

AFR records the repo around whatever tool you use. It works with local coding agents and manual workflows, including:

- Claude Code
- Codex
- Aider
- Cursor
- OpenHands
- GitHub Copilot workflows
- Any editor or terminal workflow that changes files in a git repo

## Safety Notes

- AFR records local git evidence; it does not judge whether an agent's changes are correct.
- Review diffs before sharing reports or committing code.
- Do not commit `.afr/` unless you have intentionally scrubbed the contents.
- Treat captured diffs and paths as potentially sensitive.

## License

MIT. See [`LICENSE`](LICENSE).
