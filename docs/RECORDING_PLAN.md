# Agent Flight Recorder — Recording Plan

30-second screen recording. No narration required.

---

## Before you hit record

Run setup off-screen. Use a clean throwaway repo so paths and output are predictable.

```powershell
$demo = "C:\temp\afr-demo"
Remove-Item -Recurse -Force $demo -ErrorAction SilentlyContinue
New-Item -ItemType Directory $demo | Out-Null
cd $demo
git init
git config user.email "demo@example.com"
git config user.name "AFR Demo"
"hello" | Out-File README.md -Encoding utf8
git add README.md
git commit -m "initial"
pip install -e "C:\path\to\agent-flight-recorder"
```

Clear the terminal before recording starts.

---

## Recording: exact commands to run on screen

**Step 1 — Start the session**

```powershell
afr start "Fix auth bug"
```

Pause 1 second so the output is readable.

**Step 2 — Simulate agent work**

```powershell
"session fix: token expiry check corrected" | Out-File session.py -Encoding utf8
git add session.py
"debug scratch" | Out-File scratch.txt -Encoding utf8
```

Type these at a normal pace. Viewers should see the commands, not just the results.

**Step 3 — Stop the session**

```powershell
afr stop
```

Pause 1 second on the report path output.

**Step 4 — Print the report**

```powershell
afr report
```

Let the report scroll fully. End the recording here.

---

## What to show

- The full terminal from `afr start` through `afr report`
- The report output: Mission, Duration, Branch, HEAD before/after, Files changed, Diff path, Raw evidence path
- Command prompts so viewers can see exactly what is typed

---

## What not to show

- Editor UI or IDE windows
- File explorer or directory listings (unless adding a 5th step)
- Personal project directories or real file paths from your machine
- Long install output
- Any `.afr/` internals beyond the printed report path
- Anything outside the terminal window

---

## Voiceover script (30 seconds)

Use this if recording with audio:

> "AI coding agents can change a dozen files in seconds — faster than your terminal scrollback.
> Agent Flight Recorder gives each session a black box.
> `afr start` captures the git state before.
> Run your agent. Make your changes.
> `afr stop` captures the state after, writes the diff, and generates a Markdown report.
> `afr report` prints it. Mission, duration, branch, what changed, and the raw evidence path.
> Local-first. No cloud. Three commands."

---

## Silent version — text overlay script

Use this for a no-audio screen recording with overlaid captions:

| Timestamp | On-screen action | Overlay text |
|-----------|-----------------|--------------|
| 0:00 | Terminal open, cursor ready | Agent Flight Recorder |
| 0:02 | Type `afr start "Fix auth bug"` | Start a session |
| 0:05 | Output prints | Captures git state before |
| 0:08 | Type file edits, git add | Run your agent or make changes |
| 0:14 | Type `afr stop` | Captures git state after |
| 0:17 | Report path prints | Diff and report written |
| 0:20 | Type `afr report` | Print the report |
| 0:22 | Report scrolls | Mission · Duration · Branch · Files · Diff |
| 0:28 | Report ends at Raw evidence path | Local-first. No cloud. Three commands. |

---

## Cleanup

```powershell
cd C:\
Remove-Item -Recurse -Force C:\temp\afr-demo -ErrorAction SilentlyContinue
```
