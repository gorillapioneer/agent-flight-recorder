# Special Agent Ops Integration

Special Agent Ops defines how an agent task should be controlled.
Agent Flight Recorder records what happened.

Use them together:

1. Fill out a Special Agent Ops mission brief.
2. Define safe repo boundaries.
3. Start an Agent Flight Recorder run.
4. Add the approved plan.
5. Let the agent work on a branch.
6. Capture the diff.
7. Record commands, checks, and reviewer findings.
8. Finish the run with outcome and rollback notes.
9. Build project memory from successful runs.

## Suggested Mapping

| Special Agent Ops artifact | Flight Recorder artifact |
|---|---|
| Mission brief | `mission.md`, `flight-record.json` |
| Planner output | `plan.md` |
| Safety gate result | `checks.json` |
| No-secrets result | `checks.json` |
| PR diff | `diff.patch` |
| Review notes | `final-report.md` |
| Rollback plan | `rollback.md` |
| Lessons learned | `lessons.md`, `PROJECT_MEMORY.md` |

## Rule Of Thumb

Special Agent Ops is the control tower.
Agent Flight Recorder is the black box.

Neither replaces human approval.

