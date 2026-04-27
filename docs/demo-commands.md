# Demo Commands

Use this with:

- [demo-script.md](/Users/rk/Desktop/IntentShell/docs/demo-script.md)
- [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md)

The goal is to make recording deterministic and easy to repeat.

## Off-Camera Prep

Run these before you start recording:

```bash
cd /Users/rk/Desktop/IntentShell
export RECORD_ROOT="$(mktemp -d /tmp/intentshell-recording.XXXXXX)"
python3 -m venv "$RECORD_ROOT/.venv"
source "$RECORD_ROOT/.venv/bin/activate"
python3 -m pip install .

export RM_REPO="$RECORD_ROOT/rm"
export MV_REPO="$RECORD_ROOT/mv"

mkdir "$RM_REPO" "$MV_REPO"
cp -R fixtures/demo_repo/. "$RM_REPO"
cp -R fixtures/demo_repo/. "$MV_REPO"
mkdir "$MV_REPO/archive"
```

Recommended:

- increase terminal font size before recording
- keep the terminal full-screen
- start the recording with the terminal already open in `$RM_REPO`

## Primary Recording

This is the main proof loop: mismatch, rewrite, execute, audit, restore. Each command starts with a visible section label so the recording is easy to follow.

Before the first terminal command appears, use the edit-only opening from [demo-script.md](/Users/rk/Desktop/IntentShell/docs/demo-script.md):
- show [docs/assets/financial-express-context-16x9.png](assets/financial-express-context-16x9.png) for 5-7 seconds
- show [docs/assets/devpost-thumbnail.png](assets/devpost-thumbnail.png) for about 5 seconds
- then begin the terminal sequence below with the fixture repo

The iMovie overlay `Valid command ≠ intended command` belongs on the fixture repo shot, after the first command below prints the file list.

### 1. Show the fixture repo

```bash
printf '\n--- fixture repo ---\n'
cd "$RM_REPO"
ls -1
```

### 2. Show the rewrite-required verification

```bash
printf '\n--- verify risky command ---\n'
intentshell verify \
  --cwd "$RM_REPO" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts'
```

### 3. Apply the safe rewrite

```bash
printf '\n--- apply safe rewrite ---\n'
intentshell verify \
  --cwd "$RM_REPO" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts' \
  --apply safe
```

### 4. Prove what remains

```bash
printf '\n--- remaining files ---\n'
find "$RM_REPO" -maxdepth 1 -mindepth 1 ! -name '.intentshell' -exec basename {} \; | sort
```

Expected visible result:

- `README.md`
- `config`
- `src`

### 5. Show the audit entry

```bash
printf '\n--- audit trail ---\n'
intentshell audit show latest --cwd "$RM_REPO"
```

### 6. Show the trash entry

```bash
printf '\n--- local trash ---\n'
intentshell trash list --cwd "$RM_REPO"
```

### 7. Show restore working

```bash
printf '\n--- restore deleted artifacts ---\n'
export OP_ID="$(intentshell trash list --cwd "$RM_REPO" | head -n 1 | cut -d '|' -f 1 | tr -d ' ')"
intentshell trash restore "$OP_ID" --cwd "$RM_REPO"
```

### 8. Confirm restore

```bash
printf '\n--- restored files ---\n'
find "$RM_REPO" -maxdepth 1 -mindepth 1 ! -name '.intentshell' -exec basename {} \; | sort
```

## Optional 10-Second `mv` Proof

Use this only if you want a quick extra clip showing that `mv` is already supported in the MVP. Skip it if the main `rm` story already fills the time.

```bash
printf '\n--- optional mv fixture ---\n'
cd "$MV_REPO"
ls -1

printf '\n--- optional mv verification ---\n'
intentshell verify \
  --cwd "$MV_REPO" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts'

printf '\n--- optional mv safe apply ---\n'
intentshell verify \
  --cwd "$MV_REPO" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts' \
  --apply safe
```

Optional confirmation:

```bash
printf '\n--- optional mv result ---\n'
find "$MV_REPO" -maxdepth 2 -mindepth 1 ! -path '*/.intentshell*' | sort
```

## Resetting Between Takes

If you want a fresh recording workspace, rerun only this setup block:

```bash
cd /Users/rk/Desktop/IntentShell
export RECORD_ROOT="$(mktemp -d /tmp/intentshell-recording.XXXXXX)"
python3 -m venv "$RECORD_ROOT/.venv"
source "$RECORD_ROOT/.venv/bin/activate"
python3 -m pip install .

export RM_REPO="$RECORD_ROOT/rm"
export MV_REPO="$RECORD_ROOT/mv"

mkdir "$RM_REPO" "$MV_REPO"
cp -R fixtures/demo_repo/. "$RM_REPO"
cp -R fixtures/demo_repo/. "$MV_REPO"
mkdir "$MV_REPO/archive"
```
