# Basic Run Example

This is a safe fictional run. It records a small dashboard change with a
placeholder status label.

```bash
python -m agent_flight_recorder init
```

```bash
python -m agent_flight_recorder start \
  --mission "Add an API health badge to a dashboard." \
  --agent "codex" \
  --risk-level AMBER \
  --allowed-file "src/dashboard/" \
  --planned-file "src/dashboard/ApiHealthBadge.tsx"
```

```bash
python -m agent_flight_recorder add-plan \
  --text "Add one badge, keep the change scoped, and add tests."
```

```bash
python -m agent_flight_recorder capture-diff \
  --summary "Adds a small dashboard badge and focused tests."
```

```bash
python -m agent_flight_recorder add-check \
  --name "safety gate" \
  --status pass \
  --summary "No risky patterns found."
```

```bash
python -m agent_flight_recorder add-lesson \
  --text "Keep dashboard status indicators small and easy to revert."
```

```bash
python -m agent_flight_recorder finish \
  --outcome success \
  --human-approval-status approved \
  --rollback "Revert the dashboard badge PR if the UI result is unclear."
```

```bash
python -m agent_flight_recorder build-memory
```

