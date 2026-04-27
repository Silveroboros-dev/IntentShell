# Demo Voice-Over

## Goal

Use this as the spoken companion to `docs/demo-script.md`.

Exact terminal sequence: [demo-commands.md](demo-commands.md).

The tone should be calm, direct, and lightly technical. Let the terminal output do most of the work. Do not rush to fill silence.

## Delivery Notes

- Aim for about 115-130 seconds total.
- Pause briefly after each command so the on-screen output can land.
- Stress `intent`, `policy`, `rewrite`, and `before anything runs`.
- Keep the ending crisp. Do not add extra explanation after the final line.

## Timed Script

### 0:00-0:05

"A recent reported AI-agent data-loss incident made the broader gap concrete: a destructive action can be technically authorized, but still violate intent."

### 0:05-0:10

"IntentShell starts with a narrow OS-level version of that problem: destructive file commands."

### 0:10-0:17

"Operating systems are good at checking syntax and permissions. They usually do not check whether a command matches what the user meant."

### 0:17-0:43

"That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent."

### 0:43-1:03

"For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy."

"Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs."

### 1:03-1:19

"It then proposes and applies a narrower safe rewrite that matches the stated intent."

### 1:19-1:29

"After approval, only the intended targets are deleted."

### 1:29-1:45

"Each verified run produces an audit trail, and supported deletes go to local trash."

### 1:45-1:57

"The audit trail is inspectable, and supported deletes can be restored."

### 1:57-2:07

"This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."

## One-Piece Read

"A recent reported AI-agent data-loss incident made the broader gap concrete: a destructive action can be technically authorized, but still violate intent. IntentShell starts with a narrow OS-level version of that problem: destructive file commands. Operating systems are good at checking syntax and permissions. They usually do not check whether a command matches what the user meant. That matters most for destructive file commands. Here, the user wants to delete only build artifacts, but the command is broader than that intent. For supported commands, IntentShell expands the exact target set before execution and turns that intent into an explicit policy. Here it detects that the command would also remove source code, configuration, and documentation, so the broad command requires a rewrite before anything runs. It then proposes and applies a narrower safe rewrite that matches the stated intent. After approval, only the intended targets are deleted. Each verified run produces an audit trail, and supported deletes go to local trash. The audit trail is inspectable, and supported deletes can be restored. This is not a general AI shell. It is a narrow, inspectable verification layer for destructive commands. Syntax is necessary. For destructive commands, it is not sufficient."
