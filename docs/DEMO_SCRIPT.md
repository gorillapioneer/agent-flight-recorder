# Agent Flight Recorder Demo Script

## Goal

Show the 30-60 second golden path:

```powershell
afr start "Fix auth bug"
# make a few repo changes
afr stop
afr report
```

The audience should see that Agent Flight Recorder captures the mission, before/after git state, changed files, staged and unstaged diff evidence, the report path, and the raw evidence path.

## Setup

Use a clean throwaway git repo so the demo is predictable.

```powershell
$demo = "C:\temp\afr-demo"
Remove-Item -Recurse -Force $demo -ErrorAction SilentlyContinue
mkdir $demo
cd $demo

git init
git config user.email "demo@example.com"
git config user.name "AFR Demo"

"hello" | Out-File README.md -Encoding utf8
git add README.md
git commit -m "initial"
```

Optional bash equivalent:

```bash
demo=/tmp/afr-demo
rm -rf "$demo"
mkdir -p "$demo"
cd "$demo"
git init
git config user.email "demo@example.com"
git config user.name "AFR Demo"
printf "hello\n" > README.md
git add README.md
git commit -m "initial"
```

## Demo Flow

Start recording:

```powershell
afr start "Fix auth bug"
```

Simulate agent work with one staged change, one unstaged change, and one untracked file:

```powershell
"changed" | Out-File README.md -Encoding utf8
git add README.md

"debug note" | Out-File scratch.txt -Encoding utf8
"untracked agent note" | Out-File notes.txt -Encoding utf8
```

Stop recording:

```powershell
afr stop
```

Print the report:

```powershell
afr report
```

Show the raw evidence files:

```powershell
Get-ChildItem .afr -Recurse
```

## What To Point Out

- `Mission:` shows the session goal: `Fix auth bug`.
- `Git status before:` shows the clean starting point.
- `Git status after:` shows the staged README change and untracked files.
- `Files changed:` lists the files AFR detected.
- `Diff:` points to `.afr/sessions/<timestamp>/git-diff.patch`.
- The diff block separates unstaged and staged changes.
- `Raw evidence path:` points to the session folder under `.afr/sessions/`.
- `report.md` is plain Markdown and can be pasted into a pull request, issue, or handoff note.

## 30-Second Narration

"AI coding agents can change files faster than your terminal scrollback. Agent Flight Recorder gives the session a black box: what changed, when it started, where it ended, and the raw diff."

Then run:

```powershell
afr start "Fix auth bug"
# make the demo edits
afr stop
afr report
```

End by opening the `.afr/sessions/<timestamp>/report.md` file or reading it in the terminal.

## Cleanup

```powershell
cd C:\
Remove-Item -Recurse -Force C:\temp\afr-demo -ErrorAction SilentlyContinue
```

Optional bash equivalent:

```bash
cd /
rm -rf /tmp/afr-demo
```
