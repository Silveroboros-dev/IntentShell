# Submission Assets

## Elevator Pitch

IntentShell is pre-flight safety for dangerous file commands: it checks what will change against what you meant, blocks mismatches, and suggests the safer command.

## Thumbnail

- File: [docs/assets/devpost-thumbnail.png](assets/devpost-thumbnail.png)
- Size: 1536x1024
- Ratio: 3:2

## Article Context Card

- File: [docs/assets/financial-express-context-16x9.png](assets/financial-express-context-16x9.png)
- Use as a 5-7 second opening still in the demo video.
- Purpose: problem validation for the broader failure pattern, not a claim that the current MVP would have stopped that exact API/database incident.

## Recommended Devpost Screenshots

1. Problem context
   - Use [docs/assets/financial-express-context-16x9.png](assets/financial-express-context-16x9.png) only as context, not as the project thumbnail.
   - Include the article link near it:
     `https://www.financialexpress.com/life/technology-ai-agent-just-destroyed-our-production-data-and-confessed-in-writing-founder-rings-alarm-bells-4219256/`
   - Suggested caption: `Recent AI-agent incidents show the broader failure pattern: destructive actions can be valid, authorized, and still misaligned with developer intent.`

2. Verification mismatch
   - Capture the terminal after the first `intentshell verify` command in [demo-commands.md](demo-commands.md).
   - Keep `status: rewrite_required`, the `violations:` block, and `safe rewrite: rm -rf build dist coverage` visible.

3. Audit and recovery proof
   - Capture either `intentshell audit show latest --cwd "$RM_REPO"` or `intentshell trash list --cwd "$RM_REPO"`.
   - This supports the claim that verified runs are inspectable and supported deletes can be restored.

## Video Notes

- Use [demo-commands.md](demo-commands.md) for the exact terminal sequence.
- Use [demo-voiceover.md](demo-voiceover.md) for the spoken track.
- Target length: 120-135 seconds.
- Open with a 5-7 second article-context card using [docs/assets/financial-express-context-16x9.png](assets/financial-express-context-16x9.png).
- Use the article as problem validation, not as a claim that the current MVP would have stopped that exact API/database incident.
- Add one iMovie text overlay during the fixture-repo shot: `Valid command ≠ intended command`.
- End with one simple title card: `Syntax is necessary. For destructive commands, it is not sufficient.`
- Keep the optional `mv` proof as a short extra clip only if the main `rm` loop stays under time.

## Article Context Link

Use this in the Devpost write-up or video description:

```text
Financial Express, Apr 27 2026:
https://www.financialexpress.com/life/technology-ai-agent-just-destroyed-our-production-data-and-confessed-in-writing-founder-rings-alarm-bells-4219256/
```

Suggested wording:

```text
A recent reported AI-agent data-loss incident illustrates the broader problem: destructive actions can be valid and authorized, but still violate developer intent. IntentShell starts with a narrow, inspectable version of the missing safety layer: pre-execution verification for destructive file commands.
```

## iMovie Overlay

Add the overlay as a title clip above the terminal footage:

```text
Valid command ≠ intended command
```

Recommended settings:
- title style: Standard, Lower, or another simple static title
- duration: about 4-5 seconds
- placement: lower-left or lower-third
- color: white or light gray
- motion: none or a simple fade

## Final Card

After the terminal shows `--- restored files ---`, cut to a simple black title card for about 8-10 seconds:

```text
Syntax is necessary.
For destructive commands, it is not sufficient.
```
