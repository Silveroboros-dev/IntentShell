# Demo Voice-Over

## Goal

Use this as the spoken companion to `docs/demo-script.md`.

Exact terminal sequence: [demo-commands.md](/Users/rk/Desktop/IntentShell/docs/demo-commands.md).

The tone should be calm, direct, and lightly technical. Let the terminal output do most of the work. Do not rush to fill silence.

## Delivery Notes

- Aim for about 120-135 seconds total.
- Pause briefly after each command so the on-screen output can land.
- Stress `intent`, `policy`, `rewrite`, and `before anything runs`.
- Keep the ending crisp. Do not add extra explanation after the final line.

## Timed Script

### 0:00-0:07

"A recent AI-agent data-loss story made the gap concrete: a destructive action can be valid and authorized, but still violate the developer's intent."

### 0:07-0:12

"IntentShell starts with a narrower version of that problem: destructive file commands."

### 0:12-0:19

"Operating systems are good at checking syntax and permissions. They usually do not check whether a command matches what the user meant."

### 0:19-0:45

"That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 0:45-1:05

"For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy."

"Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 1:05-1:21

"It then proposes and applies a narrower safe rewrite that matches the stated intent."

### 1:21-1:31

"After approval, only the intended targets are deleted."

### 1:31-1:47

"Each verified run produces an audit trail, and supported deletes go to local trash."

### 1:47-1:59

"The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes."

### 1:59-2:09

"This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."

## One-Piece Read

"A recent AI-agent data-loss story made the gap concrete: a destructive action can be valid and authorized, but still violate the developer's intent. IntentShell starts with a narrower version of that problem: destructive file commands. Operating systems are good at checking syntax and permissions. They usually do not check whether a command matches what the user meant. That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent. For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy. Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs. It then proposes and applies a narrower safe rewrite that matches the stated intent. After approval, only the intended targets are deleted. Each verified run produces an audit trail, and supported deletes go to local trash. The same operation can be restored, which makes the verification trail inspectable and reversible for supported deletes. This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."
