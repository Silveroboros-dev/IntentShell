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

## Supported Intent Policies

Intent policies are parsed from small explicit phrases. Unsupported intent notes are rejected rather than interpreted loosely.

Current action prefixes:
- `delete only ...`
- `remove only ...`
- `move only ...`

Current category phrases:
- generated artifacts: `build artifacts`, `generated artifacts`, `artifacts`, `temporary files`, `temp files`
- logs: `logs`, `log files`
- source code: `source`, `source code`, `source files`
- configuration: `config`, `configuration`, `config files`, `configuration files`
- documentation: `documentation`, `documentation files`, `docs`
- secrets: `secrets`, `secret files`
- user data: `user data`

Demo policies:
- `delete only build artifacts`
  - command family: `rm`
  - allowed category: `generated_artifact`
  - policy label: `delete:generated_artifact`
- `move only build artifacts`
  - command family: `mv`
  - allowed category: `generated_artifact`
  - policy label: `move:generated_artifact`

## Path Classification

Path categories are assigned by deterministic rules, not free-form language guessing. The first matching category wins.

Current classifier categories:
- `secret`
  - names such as `.env`, `.env.local`, `.env.production`, `id_rsa`, `id_ed25519`, `credentials`
  - suffixes such as `.pem`, `.key`, `.crt`, `.p12`, `.pfx`
  - paths containing `secret` or `secrets`
- `generated_artifact`
  - path parts such as `build`, `dist`, `coverage`, `out`, `target`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.parcel-cache`, `.turbo`, `.cache`, `__pycache__`
  - suffixes such as `.pyc`, `.pyo`, `.o`, `.obj`, `.tmp`, `.cache`
- `source`
  - source directories such as `src`, `app`, `lib`, `components`, `pages`, `server`, `client`, `tests`
  - source suffixes such as `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.java`, `.go`, `.rs`, `.c`, `.cc`, `.cpp`, `.h`, `.hpp`, `.cs`, `.rb`, `.php`, `.swift`, `.kt`
- `config`
  - config paths such as `config`, `configs`, `.github`, `.vscode`
  - config names such as `makefile`, `dockerfile`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `pyproject.toml`, `requirements.txt`, `docker-compose.yml`, `docker-compose.yaml`
  - suffixes such as `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.lock`
- `documentation`
  - documentation paths such as `docs`, `doc`
  - documentation names such as `readme`, `readme.md`, `license`, `license.md`, `changelog`, `changelog.md`, `contributing`, `contributing.md`
  - suffix `.md`
- `logs`
  - path parts `log` or `logs`
  - suffix `.log`
- `user_data`
  - suffixes such as `.txt`, `.rtf`, `.doc`, `.docx`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.csv`, `.tsv`
- `unknown`
  - paths that do not match an explicit category

Current demo classifications:
- `build/`, `dist/`, `coverage/` -> `generated_artifact`
- `src/` -> `source`
- `config/` -> `config`
- `README.md` -> `documentation`

## Unsupported Destructive Commands

Commands outside the supported `rm` and `mv` subsets are rejected with an explicit error instead of being interpreted loosely.
