# CLI Reference

Agent Flight Recorder is run with:

```bash
python -m agent_flight_recorder <command>
```

It has no third-party dependencies.

## `init`

Creates local storage:

- `.agent-runs/`
- `.agent-memory/`

Run evidence is ignored inside `.agent-runs/` by default because it may contain
project details. Review before sharing.

## `start`

Starts a run and creates the required run files.

Useful options:

- `--mission`
- `--agent`
- `--risk-level`
- `--allowed-file`
- `--blocked-file`
- `--planned-file`
- `--human-approval-required`

## `add-plan`

Adds plan text and planned files. Use `--text`, `--file`, or `--stdin`.

## `capture-diff`

Captures the current `git diff` into `diff.patch`.

Use `--from-file` to capture a saved patch instead.

## `add-command`

Records a command that was run outside the recorder.

The recorder does not execute commands. It logs evidence only.

## `add-check`

Records a check result with a status of:

- `pass`
- `warn`
- `fail`
- `skip`

## `add-lesson`

Adds a reusable lesson to the run.

## `finish`

Finishes the run and writes `final-report.md`.

Use `--rollback`, `--rollback-file`, or `--stdin` to provide rollback notes.

## `build-memory`

Builds `.agent-memory/PROJECT_MEMORY.md` from successful runs.

The memory firewall runs before the file is written.

