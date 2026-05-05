# Agent Flight Recorder

> **Before agents get more autonomy, they need black boxes.**

Black-box telemetry and project memory for AI coding agents: capture missions,
plans, diffs, commands, checks, outcomes, rollback paths, and lessons learned.

Agent Flight Recorder is a Python stdlib-only CLI. It writes structured run
evidence into `.agent-runs/` and builds reusable project memory in
`.agent-memory/`.

## What This Is

Agent Flight Recorder is a local evidence trail for AI coding work. It helps
you answer:

- What mission did the agent receive?
- What plan was approved?
- Which files were planned, touched, or unexpected?
- Which commands and checks were run?
- What changed in the diff?
- What was the outcome?
- How do we roll it back?
- What lesson should future agents remember?

It is designed for human-controlled workflows. The recorder captures evidence;
humans still approve plans, review diffs, and decide what merges.

## What This Is Not

- Not an autonomous agent.
- Not a replacement for human review.
- Not a secret store.
- Not a sandbox.
- Not a dependency-heavy observability stack.
- Not a guarantee that an agent change is safe.

## Why Flight Records Matter

AI coding agents often leave behind a diff and a chat transcript. That is not
enough for real engineering work.

A useful agent run should leave a black-box record:

```text
Mission
  |
  v
Plan
  |
  v
Diff + Commands + Checks
  |
  v
Outcome + Rollback
  |
  v
Lessons Learned
  |
  v
Project Memory
```

That record makes PR review easier, rollback clearer, and future agent work
less repetitive.

## Quick Start

From a project repo:

```bash
python -m agent_flight_recorder init
```

Start a run:

```bash
python -m agent_flight_recorder start \
  --mission "Add an API health badge to a dashboard." \
  --agent "codex" \
  --risk-level AMBER \
  --allowed-file "src/dashboard/" \
  --planned-file "src/dashboard/ApiHealthBadge.tsx"
```

Add the approved plan:

```bash
python -m agent_flight_recorder add-plan \
  --text "Add one small badge, tests, and no unrelated cleanup." \
  --planned-file "src/dashboard/ApiHealthBadge.test.tsx"
```

Capture the current git diff:

```bash
python -m agent_flight_recorder capture-diff \
  --summary "Adds a small dashboard health badge and focused tests."
```

Record commands and checks:

```bash
python -m agent_flight_recorder add-command \
  --command "python -m unittest" \
  --exit-code 0 \
  --note "Recorded after local verification."
```

```bash
python -m agent_flight_recorder add-check \
  --name "unit tests" \
  --status pass \
  --command "python -m unittest" \
  --summary "Relevant tests passed."
```

Finish the run:

```bash
python -m agent_flight_recorder finish \
  --outcome success \
  --human-approval-status approved \
  --diff-summary "Dashboard badge added with tests." \
  --rollback "Revert the PR if the dashboard badge causes confusion."
```

Build project memory:

```bash
python -m agent_flight_recorder build-memory
```

## CLI Commands

- `init` creates `.agent-runs/` and `.agent-memory/`.
- `start` creates a run directory and required run files.
- `add-plan` records the plan and planned files.
- `capture-diff` writes `diff.patch` from `git diff` or a patch file.
- `add-command` records a command that was run. It does not execute it.
- `add-check` records a safety check or test result.
- `add-lesson` records a lesson for future runs.
- `finish` writes rollback notes, outcome, and `final-report.md`.
- `build-memory` generates `.agent-memory/PROJECT_MEMORY.md`.

Convenience wrappers are available:

```bash
bash scripts/afr.sh --help
```

```powershell
.\scripts\afr.ps1 --help
```

## Run Files

Each run creates:

- `flight-record.json`
- `mission.md`
- `plan.md`
- `commands.log`
- `diff.patch`
- `checks.json`
- `lessons.md`
- `rollback.md`
- `final-report.md`

Run records are local evidence. Review them before sharing or committing.

## Memory Layer

`build-memory` reads successful runs and writes:

```text
.agent-memory/PROJECT_MEMORY.md
```

The memory file is intentionally short. It keeps reusable information:

- mission outcome
- files touched
- check results
- rollback notes
- lessons learned

Failed and cancelled runs are excluded by default. Use
`--include-non-success` only when a human wants those lessons included.

## Memory Firewall

Before writing memory, Agent Flight Recorder scans the generated memory text
for likely sensitive material and redacts it.

The firewall looks for:

- API key and token-like prefixes
- password or secret-like assignments
- private key blocks
- connection strings with embedded credentials
- `.env`-style sensitive lines
- broker key fields
- private or customer data placeholders

This is a guardrail, not a promise. Do not feed secrets into agent runs, and
review `.agent-memory/PROJECT_MEMORY.md` before committing it.

## Special Agent Ops Integration

Agent Flight Recorder pairs with
[Special Agent Ops](https://github.com/gorillapioneer/special-agent-ops).

Use Special Agent Ops to define the workflow:

- mission brief
- boundaries
- risk level
- PR checklist
- safety gate
- rollback expectations

Use Agent Flight Recorder to capture the evidence:

- the approved mission and plan
- what the agent actually touched
- commands and checks
- final outcome
- lessons for future runs

Together, they keep agent work reviewable and reusable without pretending that
agents replace developers.

## Roadmap

- Validate flight records against the JSON schema.
- Add richer diff summaries without storing sensitive content in memory.
- Add optional export bundles for PR review.
- Add merge-request templates for flight-record links.
- Add stricter memory firewall modes.
- Add examples for multi-agent handoff.

## License

MIT

