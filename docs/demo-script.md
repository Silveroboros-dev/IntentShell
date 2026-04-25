# 100-Second Demo Script

## Goal

Make the demo feel like live proof, not a slide presentation: OS-level problem, bad command, intent mismatch, rewrite required, safer rewrite, execution, audit, restore.

Companion spoken track: [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md).
Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

## Recording Length

Target: 95-110 seconds.

## Recording Style

- Keep the terminal visible almost the whole time.
- Use a brief thumbnail/title card, then one restrained iMovie text overlay during the problem setup.
- Show real IntentShell output instead of full-screen pipeline slides.
- Use a fresh disposable fixture copy for each destructive apply step so the recording stays deterministic.

## Recording Checklist

### 1. Title Card And OS Problem (0:00-0:05)

On screen:
- show [docs/assets/devpost-thumbnail.png](/Users/rk/Desktop/IntentShell/docs/assets/devpost-thumbnail.png)

Voiceover:
- "Operating systems are very good at checking whether a command is valid."

### 2. Show Fixture Repo (0:05-0:10)

On screen:
- `build/`
- `dist/`
- `coverage/`
- `src/`
- `config/`
- `README.md`
- iMovie overlay: `Valid command ≠ intended command`

Voiceover:
- "But they usually do not check whether it matches what the user meant."

### 3. Enter Command And Intent (0:10-0:18)

On screen:

```text
command: rm -rf ./*
intent: delete only build artifacts
```

Voiceover:
- "That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 4. Show Actual Verification State (0:18-0:35)

On screen:

```text
Expanded targets:
build  dist  coverage  src  config  README.md

Intent policy:
allowed category = generated artifacts only
```

Voiceover:
- "For supported commands, IntentShell expands the exact target set before execution and turns the intent into an explicit policy."

### 5. Show Violations And Rewrite Requirement (0:35-0:50)

On screen:

```text
Violations:
src        -> source code
config     -> configuration
README.md  -> documentation

Result: REWRITE REQUIRED — intent mismatch
```

Voiceover:
- "Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 6. Show Suggested Rewrite (0:50-1:00)

On screen:

```bash
Suggested safe rewrite:
rm -rf build dist coverage
```

Voiceover:
- "It then proposes a narrower safe rewrite that matches the stated intent."

### 7. Execute And Prove Result (1:00-1:12)

On screen:
- accept rewrite
- run command
- show remaining files: `src/`, `config/`, `README.md`

Voiceover:
- "After approval, only the intended targets are deleted."

### 8. Show Audit And Restore (1:12-1:28)

On screen:
- `intentshell audit show latest`
- `intentshell trash list`
- `intentshell trash restore <operation-id>`

Voiceover:
- "Each verified run produces an audit trail, and supported deletes can be restored."

### 9. Close (1:28-1:38)

On screen:
- `MVP now: rm subset, initial mv support, deterministic checks, inspectable verification`
- `Next: more intent policies, more risky commands`

Voiceover:
- "This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands."

### 10. Final Card (1:38-1:42)

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

## iMovie Overlay Note

Add the `Valid command ≠ intended command` line as an iMovie title above the terminal clip from roughly `0:05` to `0:10`.

Recommended style:
- simple title style, such as Standard or Lower
- white or light gray text
- lower-left or lower-third placement
- no playful animation
- duration around 4-5 seconds
