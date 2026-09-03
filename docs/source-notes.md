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
