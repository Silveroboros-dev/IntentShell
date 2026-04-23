# Demo Voice-Over

## Goal

Use this as the spoken companion to `docs/demo-script.md`.

Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

The tone should be calm, direct, and lightly technical. Let the terminal output do most of the work. Do not rush to fill silence.

## Delivery Notes

- Aim for about 75-85 seconds total.
- Pause briefly after each command so the on-screen output can land.
- Stress `blocked`, `intent`, `policy`, and `rewrite`.
- Keep the ending crisp. Do not add extra explanation after the final line.

## Timed Script

### 0:00-0:04

"IntentShell is a verification shell for destructive file operations."

### 0:04-0:10

"This repo contains generated artifacts, source code, configuration, and documentation."

### 0:10-0:18

"The user wants to delete only build artifacts, but this command is broader than that intent."

### 0:18-0:30

"For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy."

### 0:30-0:42

"Here it detects that the command would also remove source code, configuration, and documentation, so the command is blocked."

### 0:42-0:52

"It then proposes a narrower safe rewrite that matches the stated intent."

### 0:52-1:02

"After approval, only the intended targets are deleted."

### 1:02-1:12

"Each verified run produces an audit trail, and supported deletes can be restored."

### 1:12-1:20

"This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands."

### 1:20-1:24

"Syntax is necessary. For destructive commands, it is not sufficient."

## One-Piece Read

"IntentShell is a verification shell for destructive file operations. This repo contains generated artifacts, source code, configuration, and documentation. The user wants to delete only build artifacts, but this command is broader than that intent. For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy. Here it detects that the command would also remove source code, configuration, and documentation, so the command is blocked. It then proposes a narrower safe rewrite that matches the stated intent. After approval, only the intended targets are deleted. Each verified run produces an audit trail, and supported deletes can be restored. This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."
