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
