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
started_at: 2026-06-05T11:20:52
updated_at: 2026-06-05T11:51:28
objective: Make beta frontend leaner for older iPhone Safari
scope: frontend lazy loading, AGENTS.md
next_step: <ikke spesifisert>
verification: <ikke spesifisert>
blockers: ingen
```

## Resume Notes

- What is done: The repo is rolled back to `859e225b86fbb49b0e9f64ccc06f95240a8cf692`, and the heavy product release was removed.
- What remains: Product work must stay lean, R2-first, and fast to refresh.
- New rule: Product publishing must be separate from the main refresh path so sales data cannot be blocked by product errors.
- Important choices: Do not push product-related updates to `gruffsy/hibernian@beta` unless the user explicitly asks for it. Use `-IncludeSecondaryBeta` only when the user explicitly wants the secondary beta branch updated.
- Do not touch: Existing `legacy/frontend-static/data/publish/*` files unless the job is explicitly about pipeline/data refresh.
- Lean update: `frontend` now points at `product_summary.json`, the product payload stays lazy-loaded so the other pages do not pay the product cost on startup, and the compact summary is published to R2 at `latest/product_summary.json`.

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

Publish beta to primary beta remotes only:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\publish-beta.ps1 -Message "<commit message>"
```

Optional:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\publish-beta.ps1 -Message "<commit message>" -Objective "<short objective>"
powershell -ExecutionPolicy Bypass -File .\scripts\publish-beta.ps1 -Message "<commit message>" -AllowPipelineData
powershell -ExecutionPolicy Bypass -File .\scripts\publish-beta.ps1 -Message "<commit message>" -IncludeSecondaryBeta
```

Rule:
- tmux and Codex should use the script instead of editing `AGENTS.md` by hand.
- If the script is used correctly, `Current` is always updated automatically at start and finish.
- `gruffsy/hibernian@beta` stays untouched unless `-IncludeSecondaryBeta` is passed explicitly.

## History

```text
timestamp: 2026-06-03T17:57:08+02:00
owner: codex
status: complete
summary: Added the lean product pipeline scaffold, kept the secondary beta publish opt-in only, and synced the main/beta branches without touching gruffsy/hibernian@beta.
files: AGENTS.md, pipeline/sql/sales/nav_product_day_window.sql, pipeline/src/hibernian_pipeline/bootstrap/product_history.py, pipeline/src/hibernian_pipeline/build/product_day.py, pipeline/src/hibernian_pipeline/extract/nav_product_day.py, pipeline/src/hibernian_pipeline/cli.py, pipeline/src/hibernian_pipeline/publish/r2.py, pipeline/src/hibernian_pipeline/settings.py, pipeline/src/hibernian_pipeline/shared/legacy_format.py, pipeline/src/hibernian_pipeline/shared/state.py, pipeline/tests/test_legacy_format.py, pipeline/tests/test_product_pipeline.py, pipeline/tests/test_settings.py, pipeline/config/pipeline.example.json, .gitignore, scripts/publish-beta.ps1, scripts/sync-beta-remotes.ps1
next: None
```

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

### 2026-05-28T23:29:46

```text
timestamp: 2026-05-28T23:29:46
owner: codex
status: complete
summary: Removed the remaining card framing from the mobile day sections and tightened the mobile day-table spacing so the report reads more like a flat view on small screens.
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-28T23:33:26

```text
timestamp: 2026-05-28T23:33:26
owner: codex
status: complete
summary: Removed the forced horizontal overflow on the mobile day table so the columns can shrink to the viewport instead of clipping off-screen.
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-28T23:41:31

```text
timestamp: 2026-05-28T23:41:31
owner: codex
status: complete
summary: Removed the chrome collapse/scroll behavior so the navigation stays expanded and no longer responds by hiding itself when tapped or scrolled.
files: frontend/app.js
next: <ikke spesifisert>
```

### 2026-05-28T23:51:10

```text
timestamp: 2026-05-28T23:51:10
owner: codex
status: complete
summary: Added U/moms as a right-side value in the day summary cards so the mobile and desktop summaries have more balanced visual weight.
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T00:06:54

```text
timestamp: 2026-05-29T00:06:54
owner: codex
status: complete
summary: Moved DG and Per kunde into a stacked right-side block on day summary cards and tightened the day comparison table to match the compact day-table style
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T00:10:05

```text
timestamp: 2026-05-29T00:10:05
owner: codex
status: complete
summary: Added a stacked right-side metric block to the day summary cards, aligned the day comparison table with the compact day-table style, and relaxed the scope guard so it checks staged files first
files: frontend/app.js, frontend/styles.css, scripts/git-scope-guard.ps1
next: <ikke spesifisert>
```

### 2026-05-29T00:26:35

```text
timestamp: 2026-05-29T00:26:35
owner: codex
status: complete
summary: Moved the day summary back to a single U/moms side metric with DB, DG, Kunder, and Per kunde in one compact row, and tightened the day comparison table typography to better match the day table
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T09:45:27

```text
timestamp: 2026-05-29T09:45:27
owner: codex
status: complete
summary: Tightened the day summary metric row and reduced the day comparison table typography, spacing, and minimum widths to better match the compact day mobile table
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T10:11:07

```text
timestamp: 2026-05-29T10:11:07
owner: codex
status: complete
summary: Flattened the mobile comparison block so the comparison table sits more like the day-mobile-table without the extra card padding and border
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T10:21:37

```text
timestamp: 2026-05-29T10:21:37
owner: codex
status: complete
summary: Reduced the mobile day-comparison date columns slightly so the table breathes a bit more without changing the rest of the layout
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T17:52:40+02:00

```text
timestamp: 2026-05-29T17:52:40+02:00
owner: codex
status: complete
summary: Made the mobile diff table reuse the week-view shell and base table styling, removing the diff-specific mobile overrides
files: frontend/app.js, frontend/styles.css, AGENTS.md
next: None
```

### 2026-05-29T10:27:55

```text
timestamp: 2026-05-29T10:27:55
owner: codex
status: complete
summary: Narrowed the mobile amount and Akk. diff columns a little more so the comparison table breathes better on small screens
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T10:48:22

```text
timestamp: 2026-05-29T10:48:22
owner: codex
status: complete
summary: Switched the mobile day-comparison table to percentage-based column widths so it matches the compact day-mobile-table more closely
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T11:17:35

```text
timestamp: 2026-05-29T11:17:35
owner: codex
status: complete
summary: Removed the day-comparison card stack from the day page so the day view stays as one flat, uniform layout with only the visible day sections and footer
files: frontend/app.js
next: <ikke spesifisert>
```

### 2026-05-29T11:26:11

```text
timestamp: 2026-05-29T11:26:11
owner: codex
status: complete
summary: Reintroduced the day comparison tables on the day page and flattened their chrome so they sit directly in the page flow instead of inside card framing
files: frontend/app.js, frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T12:12:29

```text
timestamp: 2026-05-29T12:12:29
owner: codex
status: complete
summary: Flattened the mobile status strip, increased the spacing between the day sections, and made the comparison area feel more like part of the same mobile flow
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T12:22:51

```text
timestamp: 2026-05-29T12:22:51
owner: codex
status: complete
summary: Added consistent mobile panel treatment, spacing, and separators so the day status strip, summary sections, and comparison area read more uniformly
files: frontend/styles.css
next: <ikke spesifisert>
```

### 2026-05-29T12:56:56

```text
timestamp: 2026-05-29T12:56:56
owner: codex
status: complete
summary: Stacked the day summary metrics into left/right columns, lowercased the mobile labels, and made the day comparison tables collapsible behind the Akk. diff summary.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: Verify the mobile day page visually and tune spacing if needed
```

### 2026-05-29T13:12:59

```text
timestamp: 2026-05-29T13:12:59
owner: codex
status: complete
summary: Changed the day comparison KPI label to include the selected day and kept the comparison cards collapsible behind that summary.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: Verify the mobile day page visually and adjust the label wording if it feels too long
```

### 2026-05-29T13:21:44

```text
timestamp: 2026-05-29T13:21:43
owner: codex
status: complete
summary: Changed the comparison KPI to use the latest running difference so it shows the accumulated diff through the selected day instead of the full month total.
files: frontend/app.js,AGENTS.md
next: Verify the day comparison card still reads clearly on mobile
```

### 2026-05-29T14:06:36

```text
timestamp: 2026-05-29T14:06:36
owner: codex
status: complete
summary: Added mobile-only table detail views for week and month, compact comparison stacks for week and month, and taller finer-grained mobile charts; year keeps the table detail view without comparison.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: Review the mobile week, month, and year pages in the browser and fine-tune spacing if needed
```

### 2026-05-29T15:09:25

```text
timestamp: 2026-05-29T15:09:25
owner: codex
status: complete
summary: Made week, month, and year summary cards expand independently on mobile and added the diff card mobile table treatment so it matches the rest of the compact tables.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: Review the mobile week, month, and year pages and fine-tune spacing if needed
```

### 2026-05-31T16:20:54

```text
timestamp: 2026-05-31T16:20:54
owner: codex
status: complete
summary: Added a desktop-only wrapper around the diff table so mobile now shows only the compact diff table; kept the compact mobile diff layout intact.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: Refresh the mobile week, month, or year page and confirm the diff card no longer shows the desktop table
```

### 2026-05-31T16:43:16

```text
timestamp: 2026-05-31T16:43:16
owner: codex
status: complete
summary: Sorted chart datasets by year so 2025 appears first and separated trigger vs total diff coloring so totals use the final sign.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: <ikke spesifisert>
```

### 2026-05-31T17:21:17

```text
timestamp: 2026-05-31T17:21:17
owner: codex
status: complete
summary: Locked the mobile period-diff table styling into its own commit so the compact mobile behavior stays preserved without mixing in other changes.
files: frontend/styles.css,AGENTS.md
next: <ikke spesifisert>
```

### 2026-05-31T17:31:44

```text
timestamp: 2026-05-31T17:31:43
owner: codex
status: complete
summary: Made the desktop card layout single-column across day, week, month, year, and seller views, and preserved scroll position when comparison cards expand or collapse.
files: frontend/app.js,frontend/styles.css,AGENTS.md
next: <ikke spesifisert>
```

### 2026-05-31T19:14:37

```text
timestamp: 2026-05-31T19:14:37
owner: codex
status: complete
summary: Confirmed both beta branches were behind main, pushed main to origin/beta and hibernian/beta, and added a sync script for the normal publish flow.
files: frontend/app.js,scripts/*,AGENTS.md
next: <ikke spesifisert>
```

### 2026-05-31T22:33:42

```text
timestamp: 2026-05-31T22:33:42
owner: codex
status: complete
summary: Added a one-command beta publish script that stages changes, runs scope guard, commits, and syncs to both beta remotes.
files: scripts/publish-beta.ps1,AGENTS.md
next: Use publish-beta.ps1 for future beta releases
```

### 2026-06-02T09:17:17

```text
timestamp: 2026-06-02T09:17:17
owner: codex
status: complete
summary: Changed the day-for-day comparison to pair only actual sales days from each month, so the table skips zero-sales calendar dates and the accumulated diff follows sales-day order.
files: frontend/app.js,AGENTS.md
next: Review the comparison cards in the browser and confirm the row order matches sales-day order
```

### 2026-06-02T10:30:49

```text
timestamp: 2026-06-02T10:30:49
owner: codex
status: complete
summary: Repaired mojibake and BOM issues in the main UI, legacy UI, and pipeline text normalizers; verified no remaining mojibake markers in the touched files and compile-checked the Python files.
files: frontend/*,legacy/*,scripts/*,AGENTS.md
next: <ikke spesifisert>
```

### 2026-06-02T14:45:43

```text
timestamp: 2026-06-02T14:45:43
owner: codex
status: complete
summary: Removed browser-side mojibake repair and kept text normalization in the pipeline; verified both JS entrypoints parse cleanly.
files: frontend/app.js,legacy/frontend-static/quasarapp.js
next: <ikke spesifisert>
```

### 2026-06-03T09:40:06

```text
timestamp: 2026-06-03T09:40:06
owner: codex
status: complete
summary: Regenerated and republished data; Tønsberg now appears only once and the year chart should no longer split the store into two bars.
files: pipeline/src/hibernian_pipeline/shared/legacy_format.py,pipeline/scripts/run_refresh_r2.ps1,pipeline/scripts/publish_r2_only.ps1,legacy/frontend-static/data/publish/*
next: <ikke spesifisert>
```

### 2026-06-03T10:47:10

```text
timestamp: 2026-06-03T10:47:09
owner: codex
status: complete
summary: Added a seller date picker and derived day, month, and year rankings from the selected date so the seller page follows the same date-driven flow as day.
files: frontend/app.js
next: <ikke spesifisert>
```

### 2026-06-05T11:12:48

```text
timestamp: 2026-06-05T11:12:48
owner: codex
status: complete
summary: Fixed product SQL so refresh no longer fails on missing Gross Amount, uses transaction header date, and keeps line amounts unrounded until build; verified product-only R2 upload and SQL header-vs-line totals.
files: pipeline product SQL, product refresh verification, AGENTS.md
next: <ikke spesifisert>
```

### 2026-06-05T11:51:28

```text
timestamp: 2026-06-05T11:51:28
owner: codex
status: complete
summary: Made beta startup lighter for older iPhone Safari by loading only day/meta initially, lazy-loading seller/stock/product data by page, loading Chart.js only for chart pages, and removing risky older-Safari APIs/spread max patterns from frontend/app.js.
files: frontend lazy loading, AGENTS.md
next: <ikke spesifisert>
```
