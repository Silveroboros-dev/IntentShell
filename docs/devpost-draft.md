# Devpost Draft

## Project Title

IntentShell

## Tagline / Short Description

IntentShell is pre-flight safety for dangerous file commands: it checks what will change against what you meant, blocks mismatches, and suggests the safer command.

## One-line Description

IntentShell is a deterministic command-line verification layer for destructive commands. For supported commands, it expands the exact target set before execution, checks those paths against the user's stated intent, shows violating paths, and proposes a narrower safe rewrite.

## Inspiration

Traditional shells are excellent at checking syntax and permissions, but they do not check whether a command matches what the user actually means.

That gap is most dangerous in unfamiliar repositories, where a valid command can still remove source code, configuration, or documentation instead of only generated artifacts.

IntentShell started from a simple question: can a command-line verification layer verify destructive commands against stated intent before execution?

The project also grew out of a side exploration of how philosophy and software engineering can sharpen each other: philosophy helps articulate semantic categories and intent, while software forces those ideas into explicit policies, checks, and execution constraints.

## What It Does

IntentShell catches the gap between what someone typed and what they meant before a dangerous file command runs.

The user gives it two things: a command and a short intent note. For example:

- command: `rm -rf ./*`
- intent: `delete only build artifacts`

In the demo repo, that command would touch `build/`, `dist/`, `coverage/`, `src/`, `config/`, and `README.md`. IntentShell expands that exact target set before execution, turns the intent into an explicit policy, and classifies each path deterministically.

For this example, `build/`, `dist/`, and `coverage/` are allowed generated artifacts. `src/`, `config/`, and `README.md` are violations because they are source code, configuration, and documentation. Instead of running the broad command, IntentShell proposes:

```bash
rm -rf build dist coverage
```

If the user applies the safe rewrite, only that narrower command runs. The verification is recorded in an audit log, and supported deletes are sent to local trash so they can be restored.

The MVP is deliberately narrow: a constrained subset of `rm`, initial support for selected `mv` cases, small explicit intent templates, deterministic path classification, and rejection of unsupported destructive commands. IntentShell is not a general AI shell or an undo button; its core feature is pre-execution verification against stated intent.

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
