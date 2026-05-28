# AGENTS.md

This file is the shared handoff log for parallel sessions in this repo.

Rules:
- Read this file before starting a new job.
- Update `Current` when you start work.
- Update `Current` again when you finish or pause.
- Do not delete history unless the user asks.
- Do not overwrite another session's work. Note conflicts in `Blockers` or `Resume Notes`.

## Current

```text
status: complete
owner: codex
started_at: 2026-05-28T23:08:52
updated_at: 2026-05-28T23:11:18
objective: Rework mobile day layout to reduce card framing
scope: frontend/app.js, frontend/styles.css
next_step: <ikke spesifisert>
verification: <ikke spesifisert>
blockers: ingen
```

## Resume Notes

- What is done: The smooth menu branch is finished and pushed to origin.
- What remains: Three local pipeline data files are still modified in the worktree, but they are not part of this handoff.
- Important choices: The menu toggle stays sticky only in collapsed mode.
- Do not touch: The three `legacy/frontend-static/data/publish/*` files unless the job is explicitly about pipeline/data refresh.

## Tmux Recovery Task

Use this if a fresh tmux session cannot see the branch or loses context:

```text
Repo: C:\Users\una\Documents\New project\hibernian-beta-copy
Branch: codex/chrome-menu-smooth-collapse

Run in order:
1. cd "C:\Users\una\Documents\New project\hibernian-beta-copy"
2. git status --short
3. gh auth status
4. gh auth setup-git
5. git fetch origin --prune
6. git branch -a -vv
7. git switch --track origin/codex/chrome-menu-smooth-collapse

If the branch already exists locally:
- use `git switch codex/chrome-menu-smooth-collapse`

If Git still asks for username/password:
- run `gh auth login -h github.com`
- then run `gh auth setup-git` again
```

## Shortcut Command

If you say:

```text
Les AGENTS.md
```

the tmux session should:
1. Read `Current`.
2. If `Current.status` is `complete`, start a new job by setting `status: in_progress` with a new `objective` and `scope`.
3. If `Current` points to recovery or branch problems, follow `Tmux Recovery Task`.
4. Otherwise continue from `next_step`.
5. Write the result back to `AGENTS.md` when done.

## Commit Scope Guard

Before any commit or push, run:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\git-scope-guard.ps1 -Objective "<short objective>"
```

Rules:
- `legacy/frontend-static/data/publish/*` must not be included in UI or documentation jobs.
- Those files are only allowed when the objective clearly says pipeline, data refresh, R2, or scheduler.
- If the guard stops the job, do not continue with `git add`, `git commit`, or `git push` until the scope is cleaned up.
- For actual pipeline/data work, use `-AllowPipelineData`.

## Automatic Use

To avoid manual edits, use this script to update the file:

```text
scripts/agent-task.ps1
```

Typical usage:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode start -Owner tmux -Objective "<job>" -Scope "<files>" -NextStep "<next step>"
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode finish -Owner tmux -Objective "<job>" -Scope "<files>" -Summary "<short result>"
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode run -Owner tmux -Objective "<job>" -Scope "<files>" -Command "<command>"
```

Rule:
- tmux and Codex should use the script instead of editing `AGENTS.md` by hand.
- If the script is used correctly, `Current` is always updated automatically at start and finish.

## History

```text
timestamp: 2026-05-28T22:12:00+02:00
owner: codex
status: complete
summary: Closed the smooth-menu branch and reset the handoff file so a fresh tmux session can start a new job cleanly
files: AGENTS.md
next: None
```

```text
timestamp: 2026-05-28T21:15:01+02:00
owner: codex
status: complete
summary: Made the menu start expanded and collapse on scroll, with the toggle only in the collapsed state
files: frontend/app.js, frontend/styles.css, AGENTS.md
next: None
```

```text
timestamp: 2026-05-28T21:18:35+02:00
owner: codex
status: blocked
summary: Commit finished, but push stopped by missing GitHub authentication for origin
files: frontend/app.js, frontend/styles.css
next: Authenticate GitHub and push again
```


### 2026-05-28T22:57:33

```text
timestamp: 2026-05-28T22:57:33
owner: codex
status: complete
summary: Replaced the mobile day card stack with a compact table layout and tightened spacing for day details on mobile.
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-28T23:11:18

```text
timestamp: 2026-05-28T23:11:18
owner: codex
status: complete
summary: Flattened the mobile day sections, reduced the card framing, and tightened the mobile day table with shorter labels and compact money formatting.
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```
