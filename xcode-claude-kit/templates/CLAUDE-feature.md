# Claude Feature Rules

## Feature Purpose

Describe the feature goal and user-visible behavior.

## Allowed Files

- List files and directories that may be read or modified.

## Local Test Command

```bash
./scripts/xcode-test-one <target-or-test-filter>
```

## Architecture Notes

- Record relevant module boundaries, data flow, and design constraints.

## Avoid Paths

- `DerivedData`
- `.build`
- `SourcePackages`
- `Pods`
- `.swiftpm`
- Generated files unless explicitly in scope.
