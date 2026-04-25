# Demo Voice-Over

## Goal

Use this as the spoken companion to `docs/demo-script.md`.

Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

The tone should be calm, direct, and lightly technical. Let the terminal output do most of the work. Do not rush to fill silence.

## Delivery Notes

- Aim for about 110-125 seconds total.
- Pause briefly after each command so the on-screen output can land.
- Stress `intent`, `policy`, `rewrite`, and `before anything runs`.
- Keep the ending crisp. Do not add extra explanation after the final line.

## Timed Script

### 0:00-0:05

"Operating systems are very good at checking whether a command is valid."

### 0:05-0:12

"But they usually do not check whether it matches what the user meant."

### 0:12-0:38

"That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 0:38-0:58

"For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy."

"Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 0:58-1:14

"It then proposes and applies a narrower safe rewrite that matches the stated intent."

### 1:14-1:24

"After approval, only the intended targets are deleted."

### 1:24-1:40

"Each verified run produces an audit trail, and supported deletes go to local trash."

### 1:40-1:52

"The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes."

### 1:52-2:02

"This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."

## One-Piece Read

"Operating systems are very good at checking whether a command is valid. But they usually do not check whether it matches what the user meant. That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent. For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy. Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs. It then proposes and applies a narrower safe rewrite that matches the stated intent. After approval, only the intended targets are deleted. Each verified run produces an audit trail, and supported deletes go to local trash. The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes. This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."
