# Agent Flight Recorder Launch Checklist

Use this before publishing the repo, recording a demo, or sharing the project publicly.

## 1. Repo Basics

- [ ] README opens with the three-command flow:
  `afr start "Fix auth bug"` -> `afr stop` -> `afr report`
- [ ] `pyproject.toml` installs the `afr` console command.
- [ ] `examples/sample-report.md` exists.
- [ ] `.afr/` is gitignored.
- [ ] License file is present.

## 2. Demo Readiness

- [ ] Run `pip install -e .`.
- [ ] Run `afr --help`.
- [ ] Run `python -m agent_flight_recorder --help`.
- [ ] Run a scratch repo smoke test.
- [ ] Confirm `afr start -> afr stop -> afr report` works end to end.
- [ ] Confirm the demo shows staged, unstaged, and untracked changes.
- [ ] Confirm `report.md` and raw evidence paths are easy to point out.

## 3. Trust Checks

- [ ] No cloud service is required.
- [ ] No telemetry is collected.
- [ ] No background daemon is started.
- [ ] `.afr/` stays local.
- [ ] Raw evidence remains the source of truth.
- [ ] Reports do not replace captured logs and diffs.
- [ ] Demo repo contains no secrets or private project data.

## 4. README Checks

- [ ] Opening is clear in the first screen.
- [ ] Install instructions work on a fresh checkout.
- [ ] Quickstart uses only `afr start`, `afr stop`, and `afr report`.
- [ ] Storage layout explains `.afr/`.
- [ ] Safety notes explain that local evidence can contain sensitive diffs.
- [ ] Example report is linked.

## 5. Launch Post Checklist

- [ ] Use the short pitch: AI agents are flying blind. This is their flight recorder.
- [ ] Show the three-command flow.
- [ ] Show one report excerpt.
- [ ] Mention that it is local-first and stdlib-first.
- [ ] Mention that raw evidence is the source of truth.
- [ ] Link to the repo and the sample report.

## 6. Future Ideas Not For v0.1

- [ ] Optional local LLM summary.
- [ ] HTML report.
- [ ] asciinema or GIF demo.
- [ ] Integrations with specific agents.
- [ ] Signed release binaries.
