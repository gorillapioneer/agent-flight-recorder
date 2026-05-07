# Agent Flight Recorder — Launch Posts

---

## X / Twitter (5 options)

**Option 1 — Lead with the hook**

```
AI agents are flying blind. This is their flight recorder.

afr start "Fix auth bug"
# run Claude Code, Aider, Cursor, Codex, OpenHands...
afr stop
afr report

Local. No cloud. No daemon. Plain Markdown report.
```

---

**Option 2 — Lead with the problem**

```
Your coding agent just changed 12 files.
You saw 3 lines of output before it scrolled away.

afr gives each session a black box:
git state before + after, file list, diff, and report.md

Three commands. Nothing else required.
```

---

**Option 3 — Show the output**

```
afr report outputs:

  Mission: Fix auth bug
  Duration: 42.8s
  Branch: main -> fix-auth-bug
  HEAD before: 4f7c2a9
  HEAD after:  8a3d51e
  Files changed: session.py, test_auth.py
  Diff: .afr/sessions/.../git-diff.patch

No summary. No inference. Just evidence.
```

---

**Option 4 — Skeptic-friendly**

```
Not an agent. Not a framework. Not a platform.

afr is a 3-command wrapper:
  capture before → run your agent → capture after → write report

pip install -e .
That's it.
```

---

**Option 5 — Use-case angle**

```
Ever finish an AI coding session and not know what actually changed?

afr start → run your agent → afr stop → afr report

Full diff, file list, Markdown report ready to paste into a PR or issue.
Local-first. stdlib-only.
```

---

## LinkedIn / GitHub-style post

```
AI coding agents are fast. Faster than your terminal scrollback.

When an agent finishes a session, what do you have?
A bunch of changed files and a wall of log output you can't scroll back to.

Agent Flight Recorder is a local-first black box for coding agent sessions.
Three commands, no configuration, no cloud.

  afr start "Fix auth bug"
  # run Claude Code, Aider, Cursor, Codex, OpenHands, or any tool
  afr stop
  afr report

What you get:
- The git state before the session started
- The git state when it ended
- Which files changed
- The full staged and unstaged diff
- A plain Markdown report you can paste into a PR, issue, or handoff note
- The raw evidence path under .afr/

Raw evidence is the source of truth. Summaries are optional.
AFR does not summarize, infer, or send anything anywhere.
It just captures what happened and writes it down.

GitHub: github.com/gorillapioneer/agent-flight-recorder
```

---

## Reddit / Hacker News post

**Title:** Agent Flight Recorder – local black box recorder for AI coding agent sessions

**Body:**

```
I built a small CLI tool that wraps an AI coding session with before/after git capture.

  afr start "Fix auth bug"
  # run your agent
  afr stop
  afr report

It captures:
- branch and HEAD SHA before and after
- git status before and after
- full diff (staged and unstaged)
- list of changed files
- a report.md you can paste into a PR or issue

No cloud. No daemon. No config. It writes everything under .afr/ in your repo.
Pure Python. Uses Git through the local git CLI.

The idea is simple: agents move fast and terminal output is lossy.
This gives each session a permanent, readable evidence trail.

GitHub: github.com/gorillapioneer/agent-flight-recorder
```

---

## Taglines (5 options)

1. AI agents are flying blind. This is their flight recorder.
2. Capture what your coding agent actually did.
3. Before and after. Every session. Plain Markdown.
4. Three commands. One evidence trail.
5. Local-first black box for AI coding agent sessions.

---

## Demo video captions (5 options)

1. 30-second demo: afr start → agent runs → afr stop → afr report
2. What Agent Flight Recorder captures when you run a coding agent
3. Before and after git state, file list, and raw diff — in one Markdown report
4. No cloud. No daemon. Just a clean evidence trail from every coding session.
5. afr in 30 seconds: mission, diff, and report.md ready to paste anywhere
