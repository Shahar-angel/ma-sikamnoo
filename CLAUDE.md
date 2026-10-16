# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"מה סיכמנו?" — a POC web app for tradespeople (plumber only in this POC) that records the full job trail: initial estimate → on-site diagnosis → quote → customer approval (baseline) → mid-job additions (each approved separately) → actual work done → a "what did we agree?" summary with the diff between approved and actual. The spec is `איפיון לאפליקציה מה סיכמנו.docx` (Hebrew); it deliberately excludes WhatsApp, payments, CRM, images, voice, and user accounts. All UI text is Hebrew, RTL.

## Workflow

Every new feature gets its own git branch (e.g. `feature/<short-name>`), created before any code for it is written; never develop a feature directly on the main branch. Note: the project is not yet a git repo — `git init` (with an initial commit on `main`) is required before the first feature branch.

Always plan before executing: enter plan mode, present the plan, and only implement after it is approved. Planning is done with Opus 5.5 (`claude-opus-5-5`); execution is done with Sonnet 5.5 (`claude-sonnet-5-5`). The `opusplan` model setting (`/model opusplan`) applies this split automatically.

After every implementation, run all of the following and report the results (pass/fail with evidence, never assume):
- **E2E tests** — drive `index.html` in the browser (claude-in-chrome tools) through the full flow in both roles: open job → diagnosis → quote → customer approval → addition (approve and reject) → finish → summary, and check the totals and diff.
- **Edge cases** — e.g. empty input, text the AI doesn't recognize, removing all items, quantity 0/negative, rejected quote followed by additions, done work that differs from what was approved, Hebrew/special characters and HTML in input, page reload mid-flow (localStorage), invalid API key / network failure falling back to local parsing.
- **Regression tests** — re-run the main E2E flow to confirm previously working features still work, not only the changed part.

After any code is written, run a **security review** of the change: at minimum XSS (all user/AI text inserted into HTML must go through `esc()`), handling of the API key, and trusting AI output (items must still pass `validate()`). The project is not a git repo, so `/security-review` (which reviews a branch diff) won't work unless `git init` is run first — review the changed code directly instead.

## Running

No build, no dependencies, no tests. Open `index.html` directly in a browser. Node and jq are not installed on this machine; Python is (use `PYTHONIOENCODING=utf8` when printing Hebrew from Python in Git Bash).

To read the spec docx: unzip `word/document.xml` with Python's `zipfile` and strip `<w:t>` tags.

## Architecture (`index.html`, single file, vanilla JS)

- **`PRICES`** — the fixed price list (id → name, price, Hebrew keywords, parts). This is the *only* source of prices.
- **AI layer — the core design principle:** AI converts free text into structured data only; it never sets prices. `aiParse(text, context)` calls Claude (`callClaude`, model `claude-haiku-5-5`, direct browser call with the `anthropic-dangerous-direct-browser-access` header) when an API key is set in the settings screen, otherwise falls back to `mockParse` (keyword matching). Both pass through `validate()`, which drops any item id not in `PRICES`. Output shape: `{problem, work, parts[], actions[], items[{id,qty}], source, engine}`.
- **Human in the loop:** every AI result is rendered by `structEditor(key)` so the pro can edit fields/items before proceeding. `key` is the name of the state slot (`initial`, `diagnosis`, `pending`, `done`) and is used by `setQty`/`rmItem`/`addItem` via `S[key]`.
- **State `S`:** one object persisted to `localStorage` under `mahSikamnu` on every `render()`. Holds role, step, API key, job info, each stage's parsed result, `quote` (snapshot of diagnosis items + total), `approval`, `additions[]` (each with `status` ממתין/אושר/נדחה), and an event `log`.
- **Rendering:** `render()` rebuilds the whole page from `S` via template strings. Two roles: `proView(step)` (steps indexed per `STEPS`) and `custView()` (approval screen for quote and each addition + summary). Actions live in object `A`; async ones wrap in `busy()`.
- **Summary math:** `agreed()` = approved quote items + approved additions; `compareTable()` compares that per item against `S.done.items`. Always escape user text with `esc()` when inserting into HTML.

## Obsidian integration

Project notes live in the Obsidian vault at `C:\Users\Shahar Angel\Desktop\vault\מה סיכמנו\` (overview, spec, site structure, action log). A PostToolUse hook (`.claude/settings.local.json` → `.claude/hooks/obsidian_log.py`) appends every non-read-only tool call to `יומן פעולות.md` automatically. The hook does not update the descriptive notes — when the site's behavior changes meaningfully, update `אתר - מבנה ומצב.md` in the vault (via the obsidian MCP tools).
