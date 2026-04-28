# IntentShell

Before destructive file commands run, verify they match intent.

IntentShell is a deterministic command-line verification layer for destructive file commands. For supported commands, it expands the exact command target set before execution, checks those paths against the user's stated intent, shows violating paths, and proposes a narrower safe rewrite.

Unix can already reach the same final filesystem state with a carefully written command. IntentShell does not claim new execution power. It adds a deterministic verification step before destructive execution: intent becomes an explicit policy, the command's target set is expanded before execution, violating paths are surfaced, and a safer rewrite can be proposed and audited.

## What It Does

IntentShell is a narrow command-line verification layer for destructive file commands. The current MVP centers on a constrained subset of `rm`, with initial support for selected `mv` cases, and rejects unsupported destructive file commands rather than guessing.

Traditional command execution checks syntax, resolves paths, and relies on filesystem permissions, but it does not check whether a command matches what the user actually means.

That gap matters most on destructive file operations. A user may mean "delete only build artifacts" and still run a command that also touches source code, configuration, documentation, or user data. The shell sees a valid command and executes it.

IntentShell adds a verification layer between valid syntax and intended meaning.

IntentShell is especially useful for AI-assisted developers, new contributors, and agents operating in unfamiliar repositories. Their failure mode is often not syntax. It is issuing a valid destructive file command without fully understanding the role of every affected path.

In the MVP, intent is turned into a small explicit policy rather than inferred loosely. For example, `delete only build artifacts` means every expanded target must be classified as a generated artifact. Any target outside that class is surfaced as a concrete violation before execution.

Path classification in the MVP is deterministic and rule-based. Categories are assigned by explicit path and filename rules documented in the support matrix and implementation, not by free-form language guessing.

## Why Not Just Use Unix Directly?

| Question | Plain Unix | IntentShell |
| --- | --- | --- |
| Can reach the same final safe delete? | Yes, if the user already knows the exact paths | Yes |
| Checks a broad command against stated intent before execution? | No | Yes |
| Shows violating paths and categories? | No | Yes |
| Proposes a safer rewrite for supported cases? | Manual reasoning only | Yes |
| Produces an audit trail and recovery flow inside the tool? | Ad hoc | Yes |

The current MVP scope is intentionally narrow:
- supported destructive command families: `rm`, `mv`
- explicit intent notes such as `delete only build artifacts` and `move only build artifacts`
- deterministic target expansion before execution
- deterministic path classification
- concrete violating paths when the command is too broad
- narrower safe rewrite proposal
- audit trace for every verified run
- local trash / restore for supported deletes
- supported moves run only after validating that the destination is an allowed location inside the working tree

## Scope and Limitations

- supports constrained subsets of `rm` and `mv` in the current MVP
- supports a small explicit set of intent templates
- rejects unsupported destructive file commands rather than guessing
- only governs commands executed inside IntentShell
- acts as a guardrail for supported cases, not a general safety guarantee

This narrow scope is deliberate: for destructive file commands, predictable rejection is safer than broad but uncertain coverage.

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

CLI transcript:

```text
$ intentshell verify \
    --cwd "$DEMO_DIR/repo" \
    --command 'rm -rf ./*' \
    --intent 'delete only build artifacts'
command type: rm
status: rewrite_required
command: rm -rf ./*
intent: delete only build artifacts
policy: delete:generated_artifact
allowed categories: generated artifact
expanded targets:
  - build [generated artifact] (matches a generated-artifact directory name)
  - dist [generated artifact] (matches a generated-artifact directory name)
  - coverage [generated artifact] (matches a generated-artifact directory name)
  - src [source code] (lives in a source directory)
  - config [configuration] (matches a config path pattern)
  - README.md [documentation] (looks like project documentation)
violations:
  - src [source code] (lives in a source directory)
  - config [configuration] (matches a config path pattern)
  - README.md [documentation] (looks like project documentation)
safe rewrite: rm -rf build dist coverage
```

## How It Works

IntentShell runs a fixed verification pipeline for supported commands:

1. Parse the command.
2. Expand the exact command target set before execution.
3. Classify affected paths into explicit categories such as generated artifacts, source code, configuration, documentation, logs, secrets, and user data.
4. Check the expanded command target set against a small, explicit intent policy.
5. If the command is too broad, show concrete violating paths.
6. Propose a narrower safe rewrite.
7. Execute only the accepted safe command.
8. Write an auditable trace.
9. Send supported deletes to local trash so they can be restored, and run supported moves only after validating that the destination is an allowed location inside the working tree.

## Why It's Different

IntentShell is not just a custom shell, and it is not just deletion with recovery afterward.

Its core claim is narrower and more distinctive: destructive file commands should be checked against stated intent before execution, not only after the fact.

## Hackathon Fit

IntentShell is being built for the [Rebuilding the OS: Core System Utilities Hackathon](https://bitbuilders-code-race-apr-2026.devpost.com/).

It fits the challenge as a command-line shell / terminal utility with one distinctive behavior: pre-execution intent verification for destructive file operations.

## Design Thesis

This project grew out of a side project on how philosophy and software engineering can sharpen each other: philosophy helps articulate intent and categories, while software forces those ideas into explicit checks, policies, and execution constraints.

Computers operate on syntax; humans act through meaning and categories. When a user says "delete only build artifacts," they are naming a semantic class, not just a pathname pattern.

IntentShell is a small experiment in making that semantic layer operational inside a shell.

## Support Matrix

Exact command support is documented in [docs/support-matrix.md](docs/support-matrix.md).

## Repository Layout

Current structure:

```text
IntentShell/
  README.md
  docs/
    assets/
      devpost-thumbnail.png
    support-matrix.md
  fixtures/
    demo_repo/
  src/
    intentshell/
  tests/
```

## Run Instructions

Create an isolated environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
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

Try the same flow with a broad `mv` command that should be narrowed:

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
PYTHONPATH=src python3 -m unittest discover -s tests -v
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

Syntax is necessary. For destructive file commands, it is not sufficient.
