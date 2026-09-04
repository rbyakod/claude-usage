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

Use `--db /path/to/file.sqlite3` to serve a specific database.

Open:

- `http://127.0.0.1:4310/`
- `http://127.0.0.1:4310/claude`
- `http://127.0.0.1:4310/codex`
- `http://127.0.0.1:4310/zai`

The app stores local summaries in `data/usage.sqlite3`. It does not upload transcripts or store API keys.

## Pages

- Overview: all providers together.
- Claude: Anthropic usage and API-equivalent cost.
- Codex: Codex token and reasoning-token usage.
- Z.ai / GLM: GLM API estimate and Coding Plan credit estimate, kept separate.

## Ingest Local Data

```bash
./scripts/ingest --claude
./scripts/ingest --codex
./scripts/ingest tests/fixtures/*.jsonl
```

Use `--db /path/to/file.sqlite3` to write to a different SQLite file.
