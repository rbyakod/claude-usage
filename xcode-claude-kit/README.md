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
