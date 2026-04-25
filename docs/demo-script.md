# 2-Minute Demo Script

## Goal

Make the demo feel like live proof, not a slide presentation: OS-level problem, bad command, intent mismatch, rewrite required, safer rewrite, execution, audit, restore.

Companion spoken track: [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md).
Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

## Recording Length

Target: 110-125 seconds.

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

### 2. Fixture Repo With Overlay (0:05-0:12)

On screen:
- terminal section: `--- fixture repo ---`
- visible files: `build`, `dist`, `coverage`, `src`, `config`, `README.md`
- iMovie overlay: `Valid command ≠ intended command`

Voiceover:
- "But they usually do not check whether it matches what the user meant."

### 3. Verify Risky Command (0:12-0:38)

On screen:
- terminal section: `--- verify risky command ---`
- command line includes `--command 'rm -rf ./*'`
- command line includes `--intent 'delete only build artifacts'`
- output shows `status: rewrite_required`
- output shows `expanded targets:`

Voiceover:
- "That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 4. Policy And Violations (0:38-0:58)

On screen, in the same verification output:
- `policy: delete:generated_artifact`
- `allowed categories: generated artifact`
- violations for `src`, `config`, and `README.md`
- `safe rewrite: rm -rf build dist coverage`

Voiceover:
- "For supported commands, IntentShell expands the exact target set before execution and turns the intent into an explicit policy."

Voiceover:
- "Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 5. Apply Safe Rewrite (0:58-1:14)

On screen:
- terminal section: `--- apply safe rewrite ---`
- command includes `--apply safe`
- output shows `safe rewrite: rm -rf build dist coverage`
- output shows `executed: moved 3 path(s) to local trash`

Voiceover:
- "It then proposes and applies a narrower safe rewrite that matches the stated intent."

### 6. Prove What Remains (1:14-1:24)

On screen:
- terminal section: `--- remaining files ---`
- visible result: `README.md`, `config`, `src`

Voiceover:
- "After approval, only the intended targets are deleted."

### 7. Audit And Trash (1:24-1:40)

On screen:
- terminal section: `--- audit trail ---`
- audit output shows the same command, violations, safe rewrite, and execution record
- terminal section: `--- local trash ---`
- trash output shows `build, dist, coverage`

Voiceover:
- "Each verified run produces an audit trail, and supported deletes go to local trash."

### 8. Restore Deleted Artifacts (1:40-1:52)

On screen:
- terminal section: `--- restore deleted artifacts ---`
- output shows `Restored 3 path(s)`
- terminal section: `--- restored files ---`
- visible result: `README.md`, `build`, `config`, `coverage`, `dist`, `src`

Voiceover:
- "The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes."

### 9. Close (1:52-2:02)

On screen:
- `MVP now: rm subset, initial mv support, deterministic checks, inspectable verification`
- `Next: more intent policies, more risky commands`

Voiceover:
- "This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands."

### 10. Final Card (2:02-2:06)

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
