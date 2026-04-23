# Devpost Draft

## Project Title

IntentShell

## Tagline / Short Description

Before destructive commands run, verify they match intent.

## One-line Description

IntentShell is a deterministic verification shell for destructive file operations. For supported commands, it expands the exact target set before execution, checks those paths against the user's stated intent, shows violating paths, and proposes a narrower safe rewrite.

## Inspiration

Traditional shells are excellent at checking syntax and permissions, but they do not check whether a command matches what the user actually means.

That gap matters most on destructive operations. A user may mean "delete only build artifacts" and still run a command that also touches source code, configuration, documentation, or user data. The shell sees a valid command and executes it.

IntentShell started from a simple question: can we add a verification layer between valid syntax and intended meaning?

IntentShell is especially useful for AI-assisted developers, new contributors, and agents operating in unfamiliar repositories. Their failure mode is often not syntax. It is issuing a valid destructive command without fully understanding the role of every affected path.

There is also a deeper design thesis behind the project. Computers operate on syntax; humans act through semantic categories and intentions. When a user says "delete only build artifacts," they are naming a category, not just a pathname pattern. IntentShell is a small experiment in making that semantic layer operational inside a shell.

## What It Does

IntentShell is a narrow verification shell utility for destructive file operations. The current MVP centers on a constrained subset of `rm`, with initial support for selected `mv` cases, and rejects unsupported destructive commands rather than guessing.

Unix can already reach the same final filesystem state with a carefully written command. IntentShell does not claim new execution power. It adds a deterministic verification step before destructive execution: intent becomes an explicit policy, the command's exact target set is expanded before execution, violating paths are surfaced, and a safer rewrite can be proposed and audited.

The user enters:
- a risky command
- a short intent note

Example:
- command: `rm -rf ./*`
- intent: `delete only build artifacts`

Fixture repo:
- `build/`
- `dist/`
- `coverage/`
- `src/`
- `config/`
- `README.md`

In the MVP, intent is turned into a small explicit policy rather than inferred loosely. For example, `delete only build artifacts` means every expanded target must be classified as a generated artifact. Any target outside that class is surfaced as a concrete violation before execution.

Path classification in the MVP is deterministic and rule-based. Categories are assigned by explicit path and filename rules in the implementation, not by free-form language guessing.

IntentShell then runs a fixed verification pipeline:
1. Parse the command.
2. Expand the exact target set before execution.
3. Classify affected paths into explicit categories such as generated artifacts, source code, configuration, documentation, logs, secrets, and user data.
4. Check the expanded target set against a small, explicit intent policy.
5. If the command is too broad, show concrete violating paths.
6. Propose a narrower safe rewrite.
7. Execute only the accepted safe command.
8. Write an auditable trace.
9. Send supported deletes to local trash so they can be restored, and run supported moves only after validating that the destination is an allowed location inside the working tree.

In the example above, IntentShell flags `src/` as source code, `config/` as configuration, and `README.md` as documentation.

It then proposes a narrower safe rewrite such as:

```bash
rm -rf build dist coverage
```

The point is not to replace the shell. The point is to verify whether destructive commands match intent before damage happens.

IntentShell is intentionally narrow: it is a verifier for supported destructive commands, not a general AI shell.

This narrow scope is deliberate: for destructive commands, predictable rejection is safer than broad but uncertain coverage.

## How I Built It

IntentShell is designed as a small, inspectable system rather than a black box.

Core components:
- a terminal interface for entering commands and intent notes
- a parser for supported destructive commands
- a target expander that resolves which paths would actually be affected
- a deterministic path classifier
- an intent policy checker
- a violation generator that lists concrete mismatches
- a safe rewrite synthesizer
- an audit inspection command for reviewing prior verification runs
- a local trash store for supported deletes
- a JSONL audit log for every verified run

The architecture is intentionally narrow:
- support a small, explicit command set first: `rm` and `mv`
- keep the intent grammar small and explicit
- prefer deterministic checks over vague natural-language guessing
- make every verification step inspectable

That scope discipline is what makes the system easier to test, explain, and trust.

## Challenges I Ran Into

The hardest part was keeping the project narrow enough to stay reliable.

This idea can easily turn into:
- a full shell replacement
- a generic AI terminal assistant
- a broad conceptual essay about intent and meaning

None of those directions would preserve the reliability and clarity this project needed.

Another challenge was deciding what the novelty actually is. Trash and restore are useful, but they are not the main idea. The core feature is pre-execution intent verification with concrete violations and safe rewrite generation.

## Accomplishments That I'm Proud Of

I'm proud that IntentShell does not stop at safer deletion after the fact. It checks semantic fit before destructive execution.

I'm also proud that the philosophical thesis became a working design constraint rather than just framing. Instead of talking abstractly about meaning, the project forces meaning into explicit categories, checks, and violations that the system can act on.

## What I Learned

I learned that command parsing is not the hard part. The hard part is making semantic verification narrow enough to be dependable.

That pushed the design toward:
- explicit intent templates
- deterministic path categories
- concrete violating examples
- narrow safe rewrites

I also learned that conceptual ideas become much more useful when they are forced into an execution environment. Once the system has to decide whether a command is acceptable, vague concepts have to become precise.

## What's Next for IntentShell

Next steps:
- add a small number of other risky file operations beyond `rm` and `mv`
- expand the intent template set carefully
- improve classification accuracy across more project layouts
- add a richer fixture repo and broader golden test coverage
- make the audit trace easier to inspect visually

Longer term, the same verification pattern could apply to agent actions and deployment workflows. But the goal here is to validate the primitive first.

## Closing Line

Syntax is necessary. For destructive commands, it is not sufficient.
