# Claude Usage Workspace Design

## Goal

Build two separate local projects under `/Users/ravibyakod/WORK/Claude-Usage`:

1. `xcode-claude-kit`: a reusable Claude Code setup kit for new Xcode projects.
2. `usage-dashboards`: one local dashboard app with a shared parser/cost engine, one local server, and separate Claude, Codex, and Z.ai/GLM dashboard pages.

The 147-page source PDF is the design source. Its main constraints are: keep Claude/Xcode tasks scoped, keep build and test output compact, parse local JSONL transcripts for usage, use SQLite for local storage, label command-level token attribution as estimated, keep provider billing ledgers separate, and never store API keys.

## Non-Goals

- No cloud service.
- No transcript upload.
- No paid API calls for dashboard operation.
- No fake per-prompt subscription cost for Z.ai Coding Plan usage.
- No automatic Xcode project mutation beyond files intentionally installed by the kit.
- No attempt to make command-level token cost exact when transcript data only supports estimates.

## Global Model Mapping

Apply this mapping in docs, examples, config, dashboards, pricing seeds, shell launchers, and tests:

- `glm-5.3-flash`: lightweight/fast GLM model for all lightweight examples.
- `glm-5.3`: strong/default GLM model for all strong/default examples.

When parsing existing transcripts, preserve the recorded model ID exactly. Normalization is only for generated examples, defaults, and grouping aliases.

## Project Layout

```text
/Users/ravibyakod/WORK/Claude-Usage/
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   └── plans/
│   └── source-notes.md
├── xcode-claude-kit/
│   ├── README.md
│   ├── install.sh
│   ├── templates/
│   │   ├── CLAUDE-root.md
│   │   ├── CLAUDE-feature.md
│   │   └── task-contract.md
│   ├── scripts/
│   │   ├── xcode-build
│   │   ├── xcode-test
│   │   ├── xcode-test-one
│   │   ├── xcode-errors
│   │   ├── project-summary
│   │   └── git-summary
│   └── config/
│       ├── permissions.example.json
│       └── xcode-rules.json
└── usage-dashboards/
    ├── README.md
    ├── app/
    │   ├── server.py
    │   ├── static/
    │   │   ├── index.html
    │   │   ├── styles.css
    │   │   └── app.js
    │   └── templates/
    ├── core/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── db.py
    │   ├── ingest.py
    │   ├── claude_parser.py
    │   ├── codex_parser.py
    │   ├── attribution.py
    │   ├── costs.py
    │   └── recommendations.py
    ├── config/
    │   ├── anthropic-pricing.json
    │   ├── codex-pricing.json
    │   ├── zai-pricing.json
    │   └── thresholds.json
    ├── data/
    │   └── .gitkeep
    ├── scripts/
    │   ├── ingest
    │   └── serve
    └── tests/
        ├── fixtures/
        ├── test_claude_parser.py
        ├── test_codex_parser.py
        ├── test_costs.py
        └── test_recommendations.py
```

## Xcode Claude Kit Design

`xcode-claude-kit` is a copyable toolkit for future Xcode repositories. It is not coupled to the dashboard app.

### Root Instructions

`templates/CLAUDE-root.md` keeps global instructions compact:

- Scope file reads to the requested feature.
- Prefer `rg`, targeted file reads, and project summary scripts over broad repository dumps.
- Do not inspect `DerivedData`, `.build`, `SourcePackages`, generated files, or full simulator logs.
- Avoid manual `.xcodeproj/project.pbxproj` edits unless the task is explicitly project configuration.
- Run targeted tests during development.
- Keep command output compact.
- Preserve task, files changed, failing tests, decisions, and next actions during `/compact`.
- Use Superpowers for brainstorming, planning, TDD, debugging, verification, and review when applicable.

### Feature Instructions

`templates/CLAUDE-feature.md` gives nested feature-folder instructions for architecture, naming, local test command, and files to avoid.

### Task Contract

`templates/task-contract.md` gives a fill-in structure:

- task
- scope
- allowed files
- do-not-read paths
- smallest useful build/test command
- acceptance checks
- compact instructions

### Xcode Wrappers

The scripts execute normal local tools but return concise summaries:

- `xcode-build`: runs `xcodebuild build`, saves full logs under `/tmp/claude-xcode-kit/logs`, prints status, target, warnings count, and top compiler errors.
- `xcode-test`: runs a scheme test, supports `-only-testing`, saves the full log, prints failing tests and summary.
- `xcode-test-one`: convenience wrapper for a single XCTest case or suite.
- `xcode-errors`: extracts Swift/Xcode errors from an existing log.
- `project-summary`: reports schemes, targets, Swift package presence, and likely source/test directories without dumping project files.
- `git-summary`: compact status, branch, changed files, and recent commit list.

Wrappers must avoid printing secrets or full logs by default.

### Install Behavior

`install.sh` copies templates and scripts into a target Xcode repository only after a target path is supplied. It creates backups before overwriting existing `CLAUDE.md` or scripts. It prints every destination path it changes.

## Usage Dashboards Design

`usage-dashboards` is a single local-first app.

### Runtime

- Python standard library server on `127.0.0.1`.
- SQLite database in `usage-dashboards/data/usage.sqlite3`.
- Static HTML/CSS/JS frontend served by `app/server.py`.
- No required third-party packages.

This keeps installation reliable and avoids package-manager/network setup.

### Data Sources

Claude:

- Default scan path: `~/.claude/projects/**/*.jsonl`.
- Reads assistant usage records with input, output, cache creation, cache read, model, timestamp, project/session IDs where present.
- Reads tool events where present to estimate command attribution.

Codex:

- Default scan path: `~/.codex/sessions/**/*.jsonl`.
- Reads model, input tokens, cached input tokens, output tokens, reasoning tokens, tool calls, commands, timestamps, and working directory where present.
- Supports fixture-driven parsing because Codex JSONL record shapes can vary.

Z.ai/GLM:

- Uses Claude transcripts routed through Z.ai.
- Provider detection uses recorded model IDs beginning with `glm-` and optional route metadata from hooks or environment snapshot records.
- Generated launch examples use `ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"` and the approved `glm-5.3` / `glm-5.3-flash` defaults.
- Never captures `ANTHROPIC_AUTH_TOKEN`, `ZAI_API_KEY`, or any environment variable containing a token/key/secret.

### Storage

SQLite tables:

- `sessions`: provider, model, project, source path, started/ended timestamps.
- `turns`: session ID, prompt index, timestamp, text preview hash, status.
- `usage_records`: exact recorded token totals per assistant/model response.
- `commands`: command family, command preview, output line count, status, log path if known.
- `command_attribution`: estimated command token attribution linked to a turn.
- `cost_estimates`: provider-specific cost/credit estimates linked to usage records.
- `rate_cards`: versioned pricing and credit config.
- `reconciliations`: manually entered official provider usage snapshots.

Do not store full prompt text or full tool output by default. Store short previews, hashes, counts, paths, and summaries.

### Cost Rules

Claude:

- Show exact recorded token totals when transcript fields exist.
- Estimate API-equivalent cost from versioned Anthropic pricing config.
- Label subscription usage as plan usage, not exact dollars.

Codex:

- Show exact recorded token totals when transcript fields exist.
- Estimate cost from versioned OpenAI/Codex pricing config where model pricing is configured.
- Keep reasoning tokens separate from visible output tokens.

Z.ai:

- API mode: estimate USD from fresh input, cached input, and output rates per one million tokens.
- Coding Plan mode: estimate credits/quota burn from configured multipliers.
- Keep API spend and Coding Plan quota separate.
- Allow manual reconciliation against official Z.ai account usage.

Unknown model pricing must produce `unpriced_model`, not a guessed dollar amount.

### Command Attribution

Command-level token attribution is always estimated. The UI and exported data must say `estimated` for per-command token numbers.

Heuristics:

- Classify commands into `xcodebuild`, `swift`, `git`, `rg`, `find`, `simctl`, `log`, `npm`, `python`, `other`.
- Estimate command context pressure from output line count and character count when exact tool-result token fields are unavailable.
- Allocate turn token usage across commands by visible output weight.
- Never overwrite exact response-level token totals with attribution estimates.

### Dashboard Pages

One app, separate pages:

- `/claude`: Claude usage dashboard.
- `/codex`: Codex usage dashboard.
- `/zai`: Z.ai/GLM usage dashboard.
- `/`: overview with provider cards and navigation.

Each page shows:

- Today, week, and month totals.
- Tokens by input/output/cache/reasoning where relevant.
- Estimated cost or quota burn.
- Model breakdown.
- Project/session breakdown.
- Top expensive turns.
- Top command families.
- Xcode-specific warnings.
- Data freshness and source path status.

### Xcode Recommendations

Rules:

- `xcodebuild` output over 300 lines: recommend filtered wrapper output.
- full test suite repeated more than twice in a session: recommend targeted tests.
- `project.pbxproj`, `DerivedData`, `.build`, or `SourcePackages` read during unrelated task: flag broad exploration.
- one command estimated over 5,000 tokens: flag context-heavy operation.
- session context pressure over 70 percent when detectable: recommend `/compact` or a fresh scoped session.
- GLM task with 3 or more repair cycles: recommend model escalation or narrower prompt.

### UI Direction

The dashboard is an operational tool, not a marketing page.

- Dense, readable layout.
- Separate visual identity per provider without becoming three unrelated apps.
- Cards only for repeated metric tiles and table rows.
- Main screen starts with usable dashboard data, not a hero page.
- Clear labels for exact vs estimated data.
- No decorative gradients or ornamental filler.

## CLI Behavior

`usage-dashboards/scripts/ingest`:

- Creates or migrates SQLite DB.
- Scans configured transcript paths.
- Prints source counts, parsed record counts, skipped record counts, and DB path.

`usage-dashboards/scripts/serve`:

- Starts local server on `127.0.0.1:4310` by default.
- Accepts `--port`.
- Prints dashboard URLs.

## Verification

Minimum verification before declaring complete:

- Run parser unit tests for Claude, Codex, and Z.ai fixtures.
- Run cost tests for Anthropic, Codex, Z.ai API, Z.ai Coding Plan, and unknown pricing.
- Run recommendation tests for Xcode warnings.
- Run dashboard smoke test against the local server.
- Confirm generated examples contain only the approved GLM defaults: `glm-5.3` and `glm-5.3-flash`.
- Confirm generated files do not contain API keys or secret-looking defaults.

## Acceptance Criteria

- `/Users/ravibyakod/WORK/Claude-Usage/xcode-claude-kit` exists and is usable as a reusable Xcode Claude kit.
- `/Users/ravibyakod/WORK/Claude-Usage/usage-dashboards` exists and runs one local server.
- The dashboard app exposes separate Claude, Codex, and Z.ai pages.
- The shared parser/cost engine is used by all dashboard pages.
- GLM defaults use only `glm-5.3` and `glm-5.3-flash`.
- Existing transcript model IDs are preserved exactly when parsed.
- Costs and quotas are labeled honestly.
- All verification commands have fresh passing output before completion is claimed.
