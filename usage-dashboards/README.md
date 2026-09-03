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
