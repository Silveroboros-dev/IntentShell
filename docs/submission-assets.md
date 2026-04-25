# Submission Assets

## Elevator Pitch

IntentShell is pre-flight safety for dangerous file commands: it checks what will change against what you meant, blocks mismatches, and suggests the safer command.

## Thumbnail

- File: [docs/assets/devpost-thumbnail.png](assets/devpost-thumbnail.png)
- Size: 1536x1024
- Ratio: 3:2

## Recommended Devpost Screenshots

1. Verification mismatch
   - Capture the terminal after the first `intentshell verify` command in [demo-commands.md](demo-commands.md).
   - Keep `status: rewrite_required`, the `violations:` block, and `safe rewrite: rm -rf build dist coverage` visible.

2. Audit and recovery proof
   - Capture either `intentshell audit show latest --cwd "$RM_REPO"` or `intentshell trash list --cwd "$RM_REPO"`.
   - This supports the claim that verified runs are inspectable and supported deletes can be restored.

## Video Notes

- Use [demo-commands.md](demo-commands.md) for the exact terminal sequence.
- Use [demo-voiceover.md](demo-voiceover.md) for the spoken track.
- Target length: 110-125 seconds.
- Open with a 10-second problem setup: OS commands can be valid without matching user intent.
- Add one iMovie text overlay during the fixture-repo shot: `Valid command ≠ intended command`.
- Keep the optional `mv` proof as a short extra clip only if the main `rm` loop stays under time.

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
