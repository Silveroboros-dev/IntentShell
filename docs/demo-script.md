# 80-Second Demo Script

## Goal

Make the demo feel like live proof, not a slide presentation: bad command, intent mismatch, blocked result, safer rewrite, execution, audit, restore.

Companion spoken track: [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md).
Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

## Recording Length

Target: 75-85 seconds.

## Recording Style

- Keep the terminal visible almost the whole time.
- Use only a brief title overlay at the start and end.
- Show real IntentShell output instead of full-screen pipeline slides.
- Use a fresh disposable fixture copy for each destructive apply step so the recording stays deterministic.

## Recording Checklist

### 1. Title Overlay (0:00-0:04)

On screen:
- terminal already open
- brief overlay: `IntentShell — verify destructive commands before they run`

Voiceover:
- "IntentShell is a verification shell for destructive file operations."

### 2. Show Fixture Repo (0:04-0:10)

On screen:
- `build/`
- `dist/`
- `coverage/`
- `src/`
- `config/`
- `README.md`

Voiceover:
- "This repo contains generated artifacts, source code, configuration, and documentation."

### 3. Enter Command And Intent (0:10-0:18)

On screen:

```text
command: rm -rf ./*
intent: delete only build artifacts
```

Voiceover:
- "The user wants to delete only build artifacts, but this command is broader than that intent."

### 4. Show Actual Verification State (0:18-0:30)

On screen:

```text
Expanded targets:
build  dist  coverage  src  config  README.md

Intent policy:
allowed category = generated artifacts only
```

Voiceover:
- "For supported commands, IntentShell expands the exact target set before execution and turns the intent into an explicit policy."

### 5. Show Violations And Block (0:30-0:42)

On screen:

```text
Violations:
src        -> source code
config     -> configuration
README.md  -> documentation

Result: BLOCKED — intent mismatch
```

Voiceover:
- "Here it detects that the command would also remove source code, configuration, and documentation, so the broad command is blocked."

### 6. Show Suggested Rewrite (0:42-0:52)

On screen:

```bash
Suggested safe rewrite:
rm -rf build dist coverage
```

Voiceover:
- "It then proposes a narrower safe rewrite that matches the stated intent."

### 7. Execute And Prove Result (0:52-1:02)

On screen:
- accept rewrite
- run command
- show remaining files: `src/`, `config/`, `README.md`

Voiceover:
- "After approval, only the intended targets are deleted."

### 8. Show Audit And Restore (1:02-1:12)

On screen:
- `intentshell audit show latest`
- `intentshell trash list`
- `intentshell trash restore <operation-id>`

Voiceover:
- "Each verified run produces an audit trail, and supported deletes are recoverable."

### 9. Close (1:12-1:20)

On screen:
- `MVP now: rm subset, mv subset, deterministic checks, inspectable verification`
- `Next: more intent policies, more risky commands`

Voiceover:
- "This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands."

### 10. Final Card (1:20-1:24)

On screen:
- `Syntax is necessary. For destructive commands, it is not sufficient.`

Voiceover:
- "Syntax is necessary. For destructive commands, it is not sufficient."

## Submission Requirements Check

The recorded demo should make these points visible:
- project title and description
- the system working live
- explanation of how the system works
- enough context for the GitHub repo and run instructions to make sense
