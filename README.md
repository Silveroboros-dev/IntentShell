# IntentShell

Before destructive commands run, verify they match intent.

IntentShell is a deterministic verification shell for destructive file operations. For supported commands, it expands the exact target set before execution, checks those paths against the user's stated intent, shows violating paths, and proposes a narrower safe rewrite.

## Hackathon Fit

IntentShell is being built for the [Rebuilding the OS: Core System Utilities Hackathon](https://bitbuilders-code-race-apr-2026.devpost.com/).

It fits the challenge as a command-line shell / terminal utility with one distinctive behavior: pre-execution intent verification for destructive file operations.

## What It Does

IntentShell is a narrow verification shell utility for destructive file operations. The current MVP supports constrained subsets of `rm` and `mv` commands and rejects unsupported destructive commands rather than guessing.

Traditional shells check syntax and permissions, but they do not check whether a command matches what the user actually means.

That gap matters most on destructive operations. A user may mean "delete only build artifacts" and still run a command that also touches source code, configuration, documentation, or user data. The shell sees a valid command and executes it.

IntentShell adds a verification layer between valid syntax and intended meaning.

In the MVP, intent is turned into a small explicit policy rather than inferred loosely. For example, `delete only build artifacts` means every expanded target must be classified as a generated artifact. Any target outside that class is surfaced as a concrete violation before execution.

The current MVP scope is intentionally narrow:
- supported destructive command families: `rm`, `mv`
- explicit intent notes such as `delete only build artifacts` and `move only build artifacts`
- deterministic target expansion before execution
- deterministic path classification
- concrete violating paths when the command is too broad
- narrower safe rewrite proposal
- audit trace for every verified run
- local trash / restore for supported deletes
- structurally validated in-tree destinations for supported moves

## Demo Example

Fixture repo:
- `build/`
- `dist/`
- `coverage/`
- `src/`
- `config/`
- `README.md`

Example input:

```text
command: rm -rf ./*
intent: delete only build artifacts
```

Verification result:
- expanded targets: `build/`, `dist/`, `coverage/`, `src/`, `config/`, `README.md`
- violating paths: `src/` as source code, `config/` as configuration, and `README.md` as documentation
- proposed rewrite: `rm -rf build dist coverage`

Only the accepted safe rewrite is executed.

## How It Works

IntentShell runs a fixed verification pipeline for supported commands:

1. Parse the command.
2. Expand the exact target set before execution.
3. Classify affected paths into explicit categories such as generated artifacts, source code, configuration, documentation, logs, secrets, and user data.
4. Check the expanded target set against a small, explicit intent policy.
5. If the command is too broad, show concrete violating paths.
6. Propose a narrower safe rewrite.
7. Execute only the accepted safe command.
8. Write an auditable trace.
9. Send supported deletes to local trash so they can be restored, and execute supported moves only after destination validation.

## Why It's Different

IntentShell is not just a custom shell, and it is not just deletion with recovery afterward.

Its core claim is narrower and more distinctive: destructive commands should be checked against stated intent before execution, not only after the fact.

## Design Thesis

Computers operate on syntax; humans act through meaning and categories. When a user says "delete only build artifacts," they are naming a semantic class, not just a pathname pattern.

IntentShell is a small experiment in making that semantic layer operational inside a shell.

## Support Matrix

Exact command support is documented in [docs/support-matrix.md](/Users/rk/Desktop/IntentShell/docs/support-matrix.md).

## Repository Layout

Current structure:

```text
IntentShell/
  README.md
  docs/
    devpost-draft.md
    demo-script.md
  fixtures/
    demo_repo/
  src/
    intentshell/
  tests/
```

## Run Instructions

Install the package in editable mode:

```bash
python3 -m pip install -e .
```

Prepare a disposable demo workspace:

```bash
DEMO_DIR="$(mktemp -d /tmp/intentshell-demo.XXXXXX)"
mkdir "$DEMO_DIR/repo"
cp -R fixtures/demo_repo/. "$DEMO_DIR/repo"
```

Each `--apply safe` run changes that temp repo. For the cleanest manual testing, use a fresh disposable copy for each scenario (`rm`, `mv`, restore).

Preview a risky command against that disposable copy:

```bash
intentshell verify \
  --cwd "$DEMO_DIR/repo" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts'
```

Execute only the safe rewrite on the same copy:

```bash
intentshell verify \
  --cwd "$DEMO_DIR/repo" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts' \
  --apply safe
```

Try the same flow with a narrowed `mv` command:

```bash
mkdir "$DEMO_DIR/repo/archive"

intentshell verify \
  --cwd "$DEMO_DIR/repo" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts'

intentshell verify \
  --cwd "$DEMO_DIR/repo" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts' \
  --apply safe
```

Inspect local trash and restore the deleted artifact set:

```bash
intentshell trash list --cwd "$DEMO_DIR/repo"
intentshell trash restore <operation-id> --cwd "$DEMO_DIR/repo"
```

Inspect the audit trail without opening the JSONL file directly:

```bash
intentshell audit list --cwd "$DEMO_DIR/repo"
intentshell audit show latest --cwd "$DEMO_DIR/repo"
```

Run the automated checks:

```bash
python3 -m unittest discover -s tests -v
```

IntentShell writes local state inside the working directory:
- audit log: `.intentshell/audit.jsonl`
- local trash payloads: `.intentshell/trash/<operation-id>/`

## Current MVP Commands

Available now:
- `intentshell verify` for deterministic `rm` and `mv` verification
- `intentshell verify --apply safe` to send accepted deletes to local trash or execute accepted moves
- `intentshell audit list` and `intentshell audit show` to inspect verification history
- `intentshell trash list` to inspect prior delete operations
- `intentshell trash restore` to recover a previously trashed operation

## Closing Line

Syntax is necessary. For destructive commands, it is not sufficient.
