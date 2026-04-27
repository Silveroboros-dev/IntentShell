# 2-Minute Demo Script

## Goal

Make the demo feel like live proof, not a slide presentation: real-world problem signal, OS-level gap, bad command, intent mismatch, rewrite required, safer rewrite, execution, audit, restore.

Companion spoken track: [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md).
Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

## Recording Length

Target: 120-135 seconds.

## Recording Style

- Keep the terminal visible almost the whole time.
- Use the Financial Express article screenshot briefly as context, then a short IntentShell title card.
- Add one restrained iMovie text overlay during the problem setup.
- Show real IntentShell output instead of full-screen pipeline slides.
- Use a fresh disposable fixture copy for each destructive apply step so the recording stays deterministic.

## Recording Checklist

### 1. Real-World Context (0:00-0:07)

On screen:
- show [docs/assets/financial-express-context-16x9.png](/Users/rk/Desktop/IntentShell/docs/assets/financial-express-context-16x9.png)
- use it as a full-frame 16:9 still

Voiceover:
- "A recent AI-agent data-loss story made the gap concrete: a destructive action can be valid and authorized, but still violate the developer's intent."

Editing note:
- Include the article link in the Devpost write-up or video description:
  `https://www.financialexpress.com/life/technology-ai-agent-just-destroyed-our-production-data-and-confessed-in-writing-founder-rings-alarm-bells-4219256/`
- Do not imply the current IntentShell MVP would have prevented that database/API incident. Use it as problem validation for the same failure pattern.

### 2. Title Card And OS Problem (0:07-0:12)

On screen:
- show [docs/assets/devpost-thumbnail.png](/Users/rk/Desktop/IntentShell/docs/assets/devpost-thumbnail.png)

Voiceover:
- "IntentShell starts with a narrower version of that problem: destructive file commands."

### 3. Fixture Repo With Overlay (0:12-0:19)

On screen:
- terminal section: `--- fixture repo ---`
- visible files: `build`, `dist`, `coverage`, `src`, `config`, `README.md`
- iMovie overlay: `Valid command ≠ intended command`

Voiceover:
- "Operating systems are good at checking syntax and permissions. They usually do not check whether a command matches what the user meant."

### 4. Verify Risky Command (0:19-0:45)

On screen:
- terminal section: `--- verify risky command ---`
- command line includes `--command 'rm -rf ./*'`
- command line includes `--intent 'delete only build artifacts'`
- output shows `status: rewrite_required`
- output shows `expanded targets:`

Voiceover:
- "That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 5. Policy And Violations (0:45-1:05)

On screen, in the same verification output:
- `policy: delete:generated_artifact`
- `allowed categories: generated artifact`
- violations for `src`, `config`, and `README.md`
- `safe rewrite: rm -rf build dist coverage`

Voiceover:
- "For supported commands, IntentShell expands the exact target set before execution and turns the intent into an explicit policy."

Voiceover:
- "Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 6. Apply Safe Rewrite (1:05-1:21)

On screen:
- terminal section: `--- apply safe rewrite ---`
- command includes `--apply safe`
- output shows `safe rewrite: rm -rf build dist coverage`
- output shows `executed: moved 3 path(s) to local trash`

Voiceover:
- "It then proposes and applies a narrower safe rewrite that matches the stated intent."

### 7. Prove What Remains (1:21-1:31)

On screen:
- terminal section: `--- remaining files ---`
- visible result: `README.md`, `config`, `src`

Voiceover:
- "After approval, only the intended targets are deleted."

### 8. Audit And Trash (1:31-1:47)

On screen:
- terminal section: `--- audit trail ---`
- audit output shows the same command, violations, safe rewrite, and execution record
- terminal section: `--- local trash ---`
- trash output shows `build, dist, coverage`

Voiceover:
- "Each verified run produces an audit trail, and supported deletes go to local trash."

### 9. Restore Deleted Artifacts (1:47-1:59)

On screen:
- terminal section: `--- restore deleted artifacts ---`
- output shows `Restored 3 path(s)`
- terminal section: `--- restored files ---`
- visible result: `README.md`, `build`, `config`, `coverage`, `dist`, `src`

Voiceover:
- "The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes."

### 10. Final Card (1:59-2:09)

On screen:
```text
Syntax is necessary.
For destructive commands, it is not sufficient.
```

Voiceover:
- "This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."

## Submission Requirements Check

The recorded demo should make these points visible:
- project title and description
- the system working live
- explanation of how the system works
- enough context for the GitHub repo and run instructions to make sense

## iMovie Overlay Note

Add [docs/assets/financial-express-context-16x9.png](/Users/rk/Desktop/IntentShell/docs/assets/financial-express-context-16x9.png) as a short opening still from roughly `0:00` to `0:07`, and put the article URL in the Devpost write-up or video description.

Add the `Valid command ≠ intended command` line as an iMovie title above the terminal clip from roughly `0:12` to `0:17`.

At the end, add a simple black title card from roughly `1:59` to `2:09` with:

```text
Syntax is necessary.
For destructive commands, it is not sufficient.
```

Recommended overlay style:
- simple title style, such as Standard or Lower
- white or light gray text
- lower-left or lower-third placement
- no playful animation
- duration around 4-5 seconds

Recommended final-card style:
- black background
- centered white or light gray text
- no playful animation
- duration around 8-10 seconds
