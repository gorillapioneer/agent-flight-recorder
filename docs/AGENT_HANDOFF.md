# Agent Handoff Workflow

AFR records what happened. Memory tools help future agents remember. Keep those two jobs separate.

Use AFR as the evidence layer when handing work between ChatGPT, Codex, Claude Code, Devin, Aider, Cursor, OpenHands, or a manual terminal session.

## Basic flow

```bash
afr start "Build story inbox draft pack"
# run your coding agent or make manual changes
afr stop
afr handoff
```

`afr stop` writes the raw evidence:

```text
.afr/sessions/<timestamp-slug>/
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

`afr handoff` prints a continuation prompt that points the next agent back to the evidence.

## Memory capsule

The memory capsule is deliberately compact. It is safe to paste into another agent after review, or to feed into a separate memory system later.

It includes:

- Mission
- Outcome
- Duration
- Repo path
- Branch and HEAD movement
- Changed files
- Evidence paths
- Empty note slots for decisions, bugs, commands, and lessons

The capsule does not pretend to know why a change was made. Add human or agent notes after review.

## Handoff prompt

Use `afr handoff` when switching agents or chats.

Example:

```bash
afr handoff > handoff.md
```

Then paste `handoff.md` into the next agent.

The prompt tells the next agent to:

- Treat raw evidence as the source of truth
- Read `report.md`
- Inspect `git-diff.patch`
- Continue from the changed files
- Re-run relevant tests before trusting or merging changes

## With agentmemory or another memory server

AFR should not require a memory server. It should stay local-first and dependency-free.

A later integration can export the capsule into a memory tool:

```bash
afr remember --agentmemory
```

Until that exists, the safe manual path is:

1. Run `afr stop`.
2. Review `memory-capsule.md`.
3. Add confirmed notes.
4. Paste the capsule into the memory system or next agent.

## Product boundary

Good boundary:

```text
agentmemory helps agents remember.
AFR proves what happened.
```

That boundary keeps AFR useful even when memory systems change, break, or disagree.
