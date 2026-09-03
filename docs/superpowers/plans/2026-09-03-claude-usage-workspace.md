# Claude Usage Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `/Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit` and `/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards`.

**Architecture:** Two separate local projects live under one workspace. The Xcode kit is reusable documentation plus shell wrappers; the dashboard is one Python standard-library app with shared parsing, SQLite storage, cost estimation, recommendations, and separate Claude/Codex/Z.ai pages.

**Tech Stack:** POSIX shell, Python 3 standard library, SQLite, HTML, CSS, JavaScript, `unittest`.

**Spec:** `/Users/ravibyakod/WORK/Claude-Usage/docs/superpowers/specs/2026-09-03-claude-usage-design.md`

## Global Constraints

- Root output path is `/Users/ravibyakod/WORK/Claude-Usage`.
- Keep `xcode-claude-kit` separate from `usage-dashboards`.
- Use no required third-party packages.
- Dashboard binds to `127.0.0.1`.
- Do not upload transcripts or call paid APIs.
- Do not store full prompt text or full tool output by default.
- Do not store API keys or secret-looking defaults.
- Generated GLM defaults must be only `glm-5.3` and `glm-5.3-flash`.
- Parsed transcript model IDs must be preserved exactly.
- Command-level token attribution must be labeled estimated.
- Unknown pricing must produce `unpriced_model`, not guessed cost.

---

## File Structure

Create or modify these files:

- `README.md`: workspace overview and run instructions.
- `docs/source-notes.md`: source PDF design summary.
- `xcode-claude-kit/README.md`: kit usage.
- `xcode-claude-kit/install.sh`: safe installer.
- `xcode-claude-kit/templates/CLAUDE-root.md`: compact root Claude rules.
- `xcode-claude-kit/templates/CLAUDE-feature.md`: nested feature rules.
- `xcode-claude-kit/templates/task-contract.md`: task template.
- `xcode-claude-kit/config/permissions.example.json`: permission example.
- `xcode-claude-kit/config/xcode-rules.json`: wrapper limits and ignore paths.
- `xcode-claude-kit/scripts/xcode-build`: compact build wrapper.
- `xcode-claude-kit/scripts/xcode-test`: compact test wrapper.
- `xcode-claude-kit/scripts/xcode-test-one`: single-test wrapper.
- `xcode-claude-kit/scripts/xcode-errors`: log parser.
- `xcode-claude-kit/scripts/project-summary`: Xcode repo summary.
- `xcode-claude-kit/scripts/git-summary`: compact Git summary.
- `usage-dashboards/README.md`: dashboard usage.
- `usage-dashboards/core/__init__.py`: package marker.
- `usage-dashboards/core/models.py`: dataclasses.
- `usage-dashboards/core/db.py`: SQLite schema and queries.
- `usage-dashboards/core/claude_parser.py`: Claude transcript parser.
- `usage-dashboards/core/codex_parser.py`: Codex transcript parser.
- `usage-dashboards/core/attribution.py`: command classification and estimated attribution.
- `usage-dashboards/core/costs.py`: provider cost/credit calculators.
- `usage-dashboards/core/recommendations.py`: Xcode and model-use warnings.
- `usage-dashboards/core/ingest.py`: ingestion coordinator.
- `usage-dashboards/app/server.py`: local API/static server.
- `usage-dashboards/app/static/index.html`: dashboard shell.
- `usage-dashboards/app/static/styles.css`: operational dashboard styling.
- `usage-dashboards/app/static/app.js`: routing and rendering.
- `usage-dashboards/config/anthropic-pricing.json`: versioned Claude prices.
- `usage-dashboards/config/codex-pricing.json`: versioned Codex/OpenAI prices.
- `usage-dashboards/config/zai-pricing.json`: versioned Z.ai prices and plan multipliers.
- `usage-dashboards/config/thresholds.json`: warning thresholds.
- `usage-dashboards/data/.gitkeep`: data directory marker.
- `usage-dashboards/scripts/ingest`: CLI wrapper.
- `usage-dashboards/scripts/serve`: server wrapper.
- `usage-dashboards/tests/fixtures/claude_session.jsonl`: Claude fixture.
- `usage-dashboards/tests/fixtures/codex_session.jsonl`: Codex fixture.
- `usage-dashboards/tests/fixtures/zai_session.jsonl`: Z.ai fixture.
- `usage-dashboards/tests/test_claude_parser.py`: Claude parser tests.
- `usage-dashboards/tests/test_codex_parser.py`: Codex parser tests.
- `usage-dashboards/tests/test_costs.py`: cost tests.
- `usage-dashboards/tests/test_recommendations.py`: recommendation tests.
- `usage-dashboards/tests/test_server.py`: API smoke tests.

---

### Task 1: Workspace Skeleton And Source Notes

**Files:**
- Create: `README.md`
- Create: `docs/source-notes.md`
- Create: `xcode-claude-kit/README.md`
- Create: `usage-dashboards/README.md`
- Create: `usage-dashboards/data/.gitkeep`

**Interfaces:**
- Consumes: approved spec.
- Produces: documented folder structure for all later tasks.

- [ ] **Step 1: Create directories**

Run:

```bash
mkdir -p /Users/ravibyakod/WORK/Claude-Usage/docs
mkdir -p /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/{templates,scripts,config}
mkdir -p /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/{app/static,core,config,data,scripts,tests/fixtures}
```

- [ ] **Step 2: Write root README**

Create `/Users/ravibyakod/WORK/Claude-Usage/README.md`:

```markdown
# Claude Usage Workspace

This workspace contains two local projects:

- `xcode-claude-kit`: reusable Claude Code setup files for Xcode projects.
- `usage-dashboards`: one local server with separate Claude, Codex, and Z.ai/GLM usage dashboards.

All data stays local. The dashboards read local transcript files and store summaries in SQLite.
```

- [ ] **Step 3: Write source notes**

Create `/Users/ravibyakod/WORK/Claude-Usage/docs/source-notes.md`:

```markdown
# Source Notes

The source PDF requires these implementation rules:

- Tool output returned to Claude counts toward working context.
- Xcode builds and tests must return compact summaries, not full logs.
- Full logs should be saved on disk for later inspection.
- Claude usage should be parsed from local JSONL transcripts.
- Codex usage should be parsed from local JSONL sessions.
- SQLite should store usage summaries locally.
- Command-level token attribution is estimated, never exact.
- Z.ai API accounting and Z.ai Coding Plan accounting are separate ledgers.
- Generated GLM examples use `glm-5.3` and `glm-5.3-flash`.
- Existing transcript model IDs are preserved exactly.
```

- [ ] **Step 4: Write project READMEs**

Create `/Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/README.md`:

````markdown
# Xcode Claude Kit

Reusable Claude Code setup files for Xcode projects.

## Install Into A Project

Run:

```bash
/Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/install.sh /path/to/XcodeProject
```

The installer copies compact Claude instructions and safe Xcode helper scripts into the target repository. Existing `CLAUDE.md` files are backed up before replacement.

## Main Files

- `templates/CLAUDE-root.md`: root Claude Code rules.
- `templates/CLAUDE-feature.md`: feature-folder rules.
- `templates/task-contract.md`: scoped task template.
- `scripts/xcode-build`: compact build wrapper.
- `scripts/xcode-test`: compact test wrapper.
- `scripts/xcode-test-one`: single-test wrapper.
- `scripts/project-summary`: compact Xcode project summary.
- `scripts/git-summary`: compact Git summary.
````

Create `/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/README.md`:

````markdown
# Usage Dashboards

One local server with separate Claude, Codex, and Z.ai/GLM usage dashboards.

## Ingest Fixture Data

```bash
./scripts/ingest tests/fixtures/*.jsonl
```

## Start

```bash
./scripts/serve --port 4310
```

Open:

- `http://127.0.0.1:4310/`
- `http://127.0.0.1:4310/claude`
- `http://127.0.0.1:4310/codex`
- `http://127.0.0.1:4310/zai`

The app stores local summaries in `data/usage.sqlite3`. It does not upload transcripts or store API keys.
````

- [ ] **Step 5: Verify skeleton**

Run:

```bash
find /Users/ravibyakod/WORK/Claude-Usage -maxdepth 3 -type d | sort
```

Expected: directories for both projects, `docs`, and dashboard subfolders exist.

- [ ] **Step 6: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add README.md docs/source-notes.md xcode-claude-kit/README.md usage-dashboards/README.md usage-dashboards/data/.gitkeep
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "chore: scaffold Claude usage workspace"
```

---

### Task 2: Xcode Claude Kit Templates And Config

**Files:**
- Create: `xcode-claude-kit/templates/CLAUDE-root.md`
- Create: `xcode-claude-kit/templates/CLAUDE-feature.md`
- Create: `xcode-claude-kit/templates/task-contract.md`
- Create: `xcode-claude-kit/config/permissions.example.json`
- Create: `xcode-claude-kit/config/xcode-rules.json`
- Modify: `xcode-claude-kit/README.md`

**Interfaces:**
- Consumes: workspace skeleton.
- Produces: static kit templates used by `install.sh`.

- [ ] **Step 1: Write root Claude template**

Create `CLAUDE-root.md` with these sections:

```markdown
# Claude Xcode Rules

## Scope

- Work only in the task scope unless asked to expand.
- Prefer `rg`, targeted file reads, and project summaries.
- Do not inspect `DerivedData`, `.build`, `SourcePackages`, generated files, or full simulator logs.
- Avoid manual `.xcodeproj/project.pbxproj` edits unless the task is project configuration.

## Xcode Commands

- Prefer `./scripts/xcode-build` and `./scripts/xcode-test`.
- Run targeted tests during implementation.
- Save full logs on disk; return only concise summaries.

## Compaction

When compacting, preserve task, scope, decisions, modified files, failing tests, commands run, and next action.

## Superpowers

Use Superpowers for brainstorming, plan writing, TDD, systematic debugging, verification, and review when applicable.
```

- [ ] **Step 2: Write feature template**

Create `CLAUDE-feature.md` with fields for feature purpose, allowed files, local test command, architecture notes, and avoid paths.

- [ ] **Step 3: Write task contract**

Create `task-contract.md` with headings: Task, Scope, Allowed Files, Do Not Read, Smallest Test, Acceptance Checks, Compact Instructions.

- [ ] **Step 4: Write permission config**

Create `permissions.example.json`:

```json
{
  "allow": [
    "rg",
    "git status",
    "git diff",
    "./scripts/xcode-build",
    "./scripts/xcode-test",
    "./scripts/xcode-test-one",
    "./scripts/project-summary",
    "./scripts/git-summary"
  ],
  "ask": [
    "dependency installation",
    "provisioning profile changes",
    "signing changes",
    "device/simulator reset",
    "writes outside repository"
  ],
  "deny": [
    "reading secrets",
    "deleting branches",
    "rewriting git history",
    "removing DerivedData without approval"
  ]
}
```

- [ ] **Step 5: Write Xcode rules config**

Create `xcode-rules.json`:

```json
{
  "log_dir": "/tmp/claude-xcode-kit/logs",
  "max_summary_lines": 120,
  "warn_output_lines": 300,
  "ignore_paths": ["DerivedData", ".build", "SourcePackages", "Pods", ".swiftpm"],
  "error_patterns": ["error:", "warning:", "Test Case '-["]
}
```

- [ ] **Step 6: Verify no stale GLM defaults**

Run:

```bash
rg -n "glm-" /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit || true
```

Expected: no output. The Xcode kit does not need GLM defaults.

- [ ] **Step 7: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add xcode-claude-kit
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add Xcode Claude templates"
```

---

### Task 3: Xcode Wrapper Scripts And Installer

**Files:**
- Create: `xcode-claude-kit/scripts/xcode-errors`
- Create: `xcode-claude-kit/scripts/xcode-build`
- Create: `xcode-claude-kit/scripts/xcode-test`
- Create: `xcode-claude-kit/scripts/xcode-test-one`
- Create: `xcode-claude-kit/scripts/project-summary`
- Create: `xcode-claude-kit/scripts/git-summary`
- Create: `xcode-claude-kit/install.sh`
- Modify: `xcode-claude-kit/README.md`

**Interfaces:**
- Consumes: `config/xcode-rules.json` for documented defaults.
- Produces: executable scripts with compact output.

- [ ] **Step 1: Write `xcode-errors`**

Behavior:

```text
xcode-errors LOG_PATH
```

Prints first 80 matching lines containing `error:`, `warning:`, `failed`, or `Test Case '-[` plus final log path.

- [ ] **Step 2: Write `xcode-build`**

Behavior:

```text
xcode-build -scheme MyApp -destination "platform=iOS Simulator,name=iPhone 16"
```

Runs `xcodebuild build`, saves full log in `/tmp/claude-xcode-kit/logs`, prints `BUILD PASSED` or `BUILD FAILED`, output line count, warning count, error count, and extracted diagnostics.

- [ ] **Step 3: Write `xcode-test`**

Behavior:

```text
xcode-test -scheme MyApp -destination "platform=iOS Simulator,name=iPhone 16" -only-testing:MyAppTests/ProfileTests
```

Runs `xcodebuild test`, saves log, prints status, failing test lines, output line count, and log path.

- [ ] **Step 4: Write `xcode-test-one`**

Behavior:

```text
xcode-test-one MyApp MyAppTests/ProfileTests
```

Calls `xcode-test` with `-scheme "$1"` and `-only-testing:"$2"` while passing through extra args.

- [ ] **Step 5: Write summary scripts**

`project-summary` prints schemes from `xcodebuild -list` and top-level source/test folders. `git-summary` prints branch, compact status, changed files, and last five commits.

- [ ] **Step 6: Write installer**

`install.sh TARGET_REPO`:

- verifies target directory exists.
- creates `scripts/` in target.
- backs up existing `CLAUDE.md` to `CLAUDE.md.bak.TIMESTAMP`.
- copies `templates/CLAUDE-root.md` to `TARGET_REPO/CLAUDE.md`.
- copies scripts to `TARGET_REPO/scripts/`.
- runs `chmod +x` on copied scripts.
- prints changed paths.

- [ ] **Step 7: Shell syntax verification**

Run:

```bash
bash -n /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/install.sh
for f in /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/scripts/*; do bash -n "$f"; done
```

Expected: no syntax errors.

- [ ] **Step 8: Installer smoke test**

Run:

```bash
tmpdir="$(mktemp -d)"
/Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/install.sh "$tmpdir"
test -f "$tmpdir/CLAUDE.md"
test -x "$tmpdir/scripts/xcode-build"
test -x "$tmpdir/scripts/xcode-test"
```

Expected: all tests exit 0.

- [ ] **Step 9: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add xcode-claude-kit
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add compact Xcode wrappers"
```

---

### Task 4: Dashboard Core Models, Database, And Fixtures

**Files:**
- Create: `usage-dashboards/core/__init__.py`
- Create: `usage-dashboards/core/models.py`
- Create: `usage-dashboards/core/db.py`
- Create: `usage-dashboards/tests/fixtures/claude_session.jsonl`
- Create: `usage-dashboards/tests/fixtures/codex_session.jsonl`
- Create: `usage-dashboards/tests/fixtures/zai_session.jsonl`

**Interfaces:**
- Produces:
  - `UsageRecord(provider: str, session_id: str, turn_id: str, model: str, timestamp: str, input_tokens: int, output_tokens: int, cache_creation_tokens: int, cache_read_tokens: int, reasoning_tokens: int, project: str, source_path: str)`
  - `CommandRecord(provider: str, session_id: str, turn_id: str, command: str, output: str, status: str, timestamp: str)`
  - `connect(db_path: Path) -> sqlite3.Connection`
  - `migrate(conn: sqlite3.Connection) -> None`
  - `insert_usage(conn, record: UsageRecord) -> None`
  - `insert_command(conn, record: CommandRecord) -> None`
  - `summary(conn, provider: str | None = None) -> dict[str, object]`

- [ ] **Step 1: Write dataclasses**

Implement `UsageRecord`, `CommandRecord`, `CostEstimate`, and `Recommendation` in `models.py`.

- [ ] **Step 2: Write database schema**

`migrate()` creates `sessions`, `turns`, `usage_records`, `commands`, `command_attribution`, `cost_estimates`, `rate_cards`, and `reconciliations`.

- [ ] **Step 3: Write insert/query helpers**

Use deterministic IDs from provider/session/turn/model/timestamp/source path to keep ingestion idempotent.

- [ ] **Step 4: Create fixtures**

Claude fixture: one Anthropic assistant usage record with cache tokens and one `xcodebuild test` command.

Codex fixture: one GPT/Codex usage record with cached input and reasoning tokens.

Z.ai fixture: one Claude-routed `glm-5.3` record and one `glm-5.3-flash` record.

- [ ] **Step 5: DB smoke verification**

Run:

```bash
python3 -m unittest discover -s /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests -p "test_*.py"
```

Expected before parser tests exist: command runs and reports 0 tests or existing tests pass.

- [ ] **Step 6: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/core usage-dashboards/tests/fixtures usage-dashboards/data/.gitkeep
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add usage dashboard data model"
```

---

### Task 5: Transcript Parsers And Attribution

**Files:**
- Create: `usage-dashboards/core/claude_parser.py`
- Create: `usage-dashboards/core/codex_parser.py`
- Create: `usage-dashboards/core/attribution.py`
- Create: `usage-dashboards/tests/test_claude_parser.py`
- Create: `usage-dashboards/tests/test_codex_parser.py`

**Interfaces:**
- Consumes: `UsageRecord`, `CommandRecord`.
- Produces:
  - `parse_claude_jsonl(path: Path) -> tuple[list[UsageRecord], list[CommandRecord]]`
  - `parse_codex_jsonl(path: Path) -> tuple[list[UsageRecord], list[CommandRecord]]`
  - `classify_command(command: str) -> str`
  - `estimate_output_tokens(output: str) -> int`
  - `attribute_commands(commands: list[CommandRecord], usage: UsageRecord) -> list[dict[str, object]]`

- [ ] **Step 1: Write failing Claude parser tests**

Assert fixture returns:

- provider `anthropic` for Claude model.
- provider `zai` for `glm-` model.
- model preserved exactly as `glm-5.3`.
- input/output/cache fields populated.
- command captured with family `xcodebuild`.

- [ ] **Step 2: Implement Claude parser**

Handle common shapes:

```python
usage = message.get("usage") or data.get("usage") or {}
model = data.get("model") or message.get("model") or "unknown"
```

Tool commands are pulled from fields named `command`, `cmd`, `tool_input.command`, or text blocks with shell command metadata.

- [ ] **Step 3: Write failing Codex parser tests**

Assert fixture returns:

- provider `codex`.
- model preserved.
- reasoning tokens populated.
- command captured.

- [ ] **Step 4: Implement Codex parser**

Handle common token field names:

- `input_tokens`
- `cached_input_tokens`
- `cache_read_input_tokens`
- `output_tokens`
- `reasoning_tokens`

- [ ] **Step 5: Implement attribution tests**

Assert command classifier maps `xcodebuild test`, `swift test`, `git diff`, `rg ViewModel`, `xcrun simctl`, and `log stream` to expected families.

- [ ] **Step 6: Implement attribution**

Use `max(1, len(output) // 4)` as approximate token pressure. Attribute by command output size while preserving exact usage totals separately.

- [ ] **Step 7: Verify parser tests**

Run:

```bash
python3 -m unittest /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/test_claude_parser.py /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/test_codex_parser.py
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/core usage-dashboards/tests
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: parse Claude and Codex usage transcripts"
```

---

### Task 6: Cost Engine And Xcode Recommendations

**Files:**
- Create: `usage-dashboards/core/costs.py`
- Create: `usage-dashboards/core/recommendations.py`
- Create: `usage-dashboards/config/anthropic-pricing.json`
- Create: `usage-dashboards/config/codex-pricing.json`
- Create: `usage-dashboards/config/zai-pricing.json`
- Create: `usage-dashboards/config/thresholds.json`
- Create: `usage-dashboards/tests/test_costs.py`
- Create: `usage-dashboards/tests/test_recommendations.py`

**Interfaces:**
- Consumes: `UsageRecord`, `CommandRecord`.
- Produces:
  - `estimate_cost(record: UsageRecord, config_dir: Path, billing_mode: str = "api") -> CostEstimate`
  - `recommendations_for(commands: list[CommandRecord], usage: list[UsageRecord], thresholds: dict[str, int]) -> list[Recommendation]`

- [ ] **Step 1: Write pricing configs**

Include model entries:

- Anthropic example entries for `claude-sonnet-4-5` and `claude-haiku-4-5`.
- Codex/OpenAI example entries for `gpt-5.6-sol` and `gpt-5.4-mini`.
- Z.ai entries for `glm-5.3` and `glm-5.3-flash`.

Use explicit `"rate_version": "2026-09-03-local-config"` and mark values as editable local estimates.

- [ ] **Step 2: Write cost tests**

Assert:

- Anthropic API cost has USD and confidence `priced_token_estimate`.
- Codex API cost has USD and confidence `priced_token_estimate`.
- Z.ai API cost uses fresh input, cached input, and output.
- Z.ai Coding Plan returns credits and no actual USD.
- Unknown model returns confidence `unpriced_model`.

- [ ] **Step 3: Implement cost engine**

Do integer-safe calculations:

```python
cost = tokens * rate_per_million / 1_000_000
```

Round display values only at API/UI boundary.

- [ ] **Step 4: Write thresholds**

Create:

```json
{
  "warn_output_lines": 300,
  "warn_estimated_command_tokens": 5000,
  "warn_context_percent": 70,
  "warn_full_test_repeats": 2,
  "warn_glm_repair_cycles": 3
}
```

- [ ] **Step 5: Write recommendation tests**

Assert warnings for verbose `xcodebuild`, repeated full tests, broad paths, high estimated command tokens, and GLM repair cycles.

- [ ] **Step 6: Implement recommendations**

Return `Recommendation` objects with `severity`, `title`, `detail`, and `source`.

- [ ] **Step 7: Verify cost and recommendation tests**

Run:

```bash
python3 -m unittest /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/test_costs.py /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/test_recommendations.py
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/core usage-dashboards/config usage-dashboards/tests
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add usage cost and recommendation engine"
```

---

### Task 7: Ingestion CLI

**Files:**
- Create: `usage-dashboards/core/ingest.py`
- Create: `usage-dashboards/scripts/ingest`
- Modify: `usage-dashboards/README.md`

**Interfaces:**
- Consumes: parsers and DB helpers.
- Produces:
  - `ingest_paths(paths: list[Path], db_path: Path) -> dict[str, int]`
  - CLI `scripts/ingest [--db PATH] [--claude] [--codex] [PATH ...]`

- [ ] **Step 1: Write ingestion implementation**

For each `.jsonl` path:

- choose parser by path hint or record shape.
- migrate DB.
- insert usage and commands idempotently.
- return counts: `files_seen`, `files_parsed`, `usage_records`, `commands`, `skipped_lines`.

- [ ] **Step 2: Write CLI wrapper**

Executable shell wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$ROOT" python3 -m core.ingest "$@"
```

- [ ] **Step 3: Fixture ingestion verification**

Run:

```bash
/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/scripts/ingest --db /tmp/claude-usage-test.sqlite3 /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/fixtures/*.jsonl
```

Expected: output includes parsed files, usage records, commands, and DB path.

- [ ] **Step 4: Verify DB has rows**

Run:

```bash
sqlite3 /tmp/claude-usage-test.sqlite3 "select provider, count(*) from usage_records group by provider order by provider;"
```

Expected: rows for `anthropic`, `codex`, and `zai`.

- [ ] **Step 5: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/core/ingest.py usage-dashboards/scripts/ingest usage-dashboards/README.md
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add transcript ingestion CLI"
```

---

### Task 8: Local Dashboard Server And API

**Files:**
- Create: `usage-dashboards/app/server.py`
- Create: `usage-dashboards/scripts/serve`
- Create: `usage-dashboards/tests/test_server.py`
- Modify: `usage-dashboards/README.md`

**Interfaces:**
- Consumes: DB helpers and cost/recommendation engine.
- Produces endpoints:
  - `GET /api/summary`
  - `GET /api/summary?provider=anthropic`
  - `GET /api/summary?provider=codex`
  - `GET /api/summary?provider=zai`
  - `GET /api/recommendations`
  - static routes `/`, `/claude`, `/codex`, `/zai`

- [ ] **Step 1: Write server tests**

Use `unittest` with a temp SQLite DB. Assert `/api/summary` returns JSON with provider totals and `/claude`, `/codex`, `/zai` return HTML.

- [ ] **Step 2: Implement server**

Use `http.server.ThreadingHTTPServer`. Serve static files and JSON API. Default DB path is `usage-dashboards/data/usage.sqlite3`.

- [ ] **Step 3: Write serve wrapper**

Executable shell wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH="$ROOT" python3 "$ROOT/app/server.py" "$@"
```

- [ ] **Step 4: Verify server tests**

Run:

```bash
python3 -m unittest /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/test_server.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/app/server.py usage-dashboards/scripts/serve usage-dashboards/tests/test_server.py usage-dashboards/README.md
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add local usage dashboard server"
```

---

### Task 9: Dashboard Frontend

**Files:**
- Create: `usage-dashboards/app/static/index.html`
- Create: `usage-dashboards/app/static/styles.css`
- Create: `usage-dashboards/app/static/app.js`
- Modify: `usage-dashboards/README.md`

**Interfaces:**
- Consumes: `/api/summary` and `/api/recommendations`.
- Produces: overview, Claude, Codex, and Z.ai pages rendered by static JS.

- [ ] **Step 1: Build HTML shell**

Include nav links for Overview, Claude, Codex, and Z.ai/GLM. Include metric area, model table, command table, recommendation list, and freshness footer.

- [ ] **Step 2: Build CSS**

Use restrained operational styling:

- dense tables.
- small metric tiles.
- clear exact/estimated labels.
- no decorative gradients.
- no landing-page hero.
- responsive layout that does not overlap at mobile width.

- [ ] **Step 3: Build JS renderer**

Detect page from `location.pathname`, fetch provider-specific summary, render:

- total tokens.
- input/output/cache/reasoning.
- estimated cost or quota.
- model breakdown.
- command families.
- recommendations.

- [ ] **Step 4: Frontend smoke verification**

Run server:

```bash
/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/scripts/serve --port 4310 --db /tmp/claude-usage-test.sqlite3
```

Then request pages:

```bash
curl -s http://127.0.0.1:4310/ | head
curl -s http://127.0.0.1:4310/claude | head
curl -s http://127.0.0.1:4310/codex | head
curl -s http://127.0.0.1:4310/zai | head
curl -s http://127.0.0.1:4310/api/summary
```

Expected: HTML pages and JSON summary return successfully.

- [ ] **Step 5: Commit**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards/app/static usage-dashboards/README.md
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "feat: add provider usage dashboards"
```

---

### Task 10: Final Verification And Hardening

**Files:**
- Modify: files only if verification exposes defects.

**Interfaces:**
- Consumes: all earlier tasks.
- Produces: verified project ready to use.

- [ ] **Step 1: Run all dashboard tests**

```bash
python3 -m unittest discover -s /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests -p "test_*.py"
```

Expected: all tests pass.

- [ ] **Step 2: Run shell syntax checks**

```bash
bash -n /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/install.sh
for f in /Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit/scripts/* /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/scripts/*; do bash -n "$f"; done
```

Expected: no syntax errors.

- [ ] **Step 3: Run fixture ingestion**

```bash
rm -f /tmp/claude-usage-test.sqlite3
/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/scripts/ingest --db /tmp/claude-usage-test.sqlite3 /Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/tests/fixtures/*.jsonl
sqlite3 /tmp/claude-usage-test.sqlite3 "select provider, count(*) from usage_records group by provider order by provider;"
```

Expected: `anthropic`, `codex`, and `zai` rows exist.

- [ ] **Step 4: Run stale GLM scan**

```bash
rg -n "glm-4|glm-5\\.1|glm-5\\.2" /Users/ravibyakod/WORK/Claude-Usage --glob '!docs/superpowers/specs/2026-09-03-claude-usage-design.md' --glob '!docs/superpowers/plans/2026-09-03-claude-usage-workspace.md'
```

Expected: no output.

- [ ] **Step 5: Run secret scan**

```bash
rg -n "(API_KEY|AUTH_TOKEN|SECRET|sk-[A-Za-z0-9]|ZAI_API_KEY|ANTHROPIC_AUTH_TOKEN)\\s*=\\s*['\\\"][^'$<]" /Users/ravibyakod/WORK/Claude-Usage
```

Expected: no hardcoded secret values.

- [ ] **Step 6: Run local server smoke**

```bash
/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards/scripts/serve --port 4310 --db /tmp/claude-usage-test.sqlite3
```

In another shell:

```bash
curl -s http://127.0.0.1:4310/api/summary
curl -s http://127.0.0.1:4310/api/recommendations
curl -s http://127.0.0.1:4310/zai
```

Expected: JSON endpoints and Z.ai dashboard page respond.

- [ ] **Step 7: Final status check**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage status --short
```

Expected: only intentionally untracked pre-existing files may remain.

- [ ] **Step 8: Commit verification fixes if any**

```bash
git -C /Users/ravibyakod/WORK/Claude-Usage status --short
git -C /Users/ravibyakod/WORK/Claude-Usage add usage-dashboards xcode-claude-kit README.md docs/source-notes.md
git -C /Users/ravibyakod/WORK/Claude-Usage commit -m "fix: harden Claude usage workspace"
```

Use this only if Step 1-6 required code changes.
