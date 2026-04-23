# IntentShell Support Matrix

IntentShell is intentionally narrow. Unsupported destructive commands are rejected rather than guessed.

## Supported `rm`

- executable: `rm`
- supported short flags: `-r`, `-R`, `-f`, `-v`
- supported long flags: `--recursive`, `--force`, `--verbose`
- operands: one or more file paths or globs
- scope: targets must resolve inside the selected `--cwd`
- directory deletes: require `-r` or `-R`
- `--apply safe`: moves only the accepted safe target set into local trash

## Unsupported `rm`

- unsupported flags such as `-i`
- targets outside `--cwd`
- commands that expand to no targets
- any destructive command outside the supported `rm` subset

## Supported `mv`

- executable: `mv`
- supported flags: `-v`, `--verbose`
- operands: one or more source paths or globs plus one destination
- scope: sources and destination must resolve inside the selected `--cwd`
- multiple sources: require an existing destination directory
- `--apply safe`: executes only the accepted safe rewrite

## Unsupported `mv`

- unsupported flags
- destination globs
- destinations outside `--cwd`
- overwrite semantics
- moves into a source's own descendant
- missing destination parent directories

## Unsupported Destructive Commands

Commands outside the supported `rm` and `mv` subsets are rejected with an explicit error instead of being interpreted loosely.
