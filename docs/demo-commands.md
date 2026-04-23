# Demo Commands

Use this with:

- [demo-script.md](/Users/rk/Desktop/IntentShell/docs/demo-script.md)
- [demo-voiceover.md](/Users/rk/Desktop/IntentShell/docs/demo-voiceover.md)

The goal is to make recording deterministic and easy to repeat.

## Off-Camera Prep

Run these before you start recording:

```bash
cd /Users/rk/Desktop/IntentShell
python3 -m pip install -e .

export RECORD_ROOT="$(mktemp -d /tmp/intentshell-recording.XXXXXX)"
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

## Primary 80-Second Recording

This is the main proof loop: block, rewrite, execute, audit, restore.

### 1. Show the fixture repo

```bash
cd "$RM_REPO"
ls -1
```

### 2. Show the blocked verification

```bash
intentshell verify \
  --cwd "$RM_REPO" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts'
```

### 3. Apply the safe rewrite

```bash
intentshell verify \
  --cwd "$RM_REPO" \
  --command 'rm -rf ./*' \
  --intent 'delete only build artifacts' \
  --apply safe
```

### 4. Prove what remains

```bash
find "$RM_REPO" -maxdepth 1 -mindepth 1 ! -name '.intentshell' -exec basename {} \; | sort
```

Expected visible result:

- `README.md`
- `config`
- `src`

### 5. Show the audit entry

```bash
intentshell audit show latest --cwd "$RM_REPO"
```

### 6. Show the trash entry

```bash
intentshell trash list --cwd "$RM_REPO"
```

### 7. Show restore working

```bash
export OP_ID="$(intentshell trash list --cwd "$RM_REPO" | head -n 1 | cut -d '|' -f 1 | tr -d ' ')"
intentshell trash restore "$OP_ID" --cwd "$RM_REPO"
```

Optional confirmation:

```bash
find "$RM_REPO" -maxdepth 1 -mindepth 1 ! -name '.intentshell' -exec basename {} \; | sort
```

## Optional 10-Second `mv` Proof

Use this only if you want a quick extra clip showing that `mv` is already supported in the MVP.

```bash
cd "$MV_REPO"
ls -1

intentshell verify \
  --cwd "$MV_REPO" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts'

intentshell verify \
  --cwd "$MV_REPO" \
  --command 'mv build src archive' \
  --intent 'move only build artifacts' \
  --apply safe
```

Optional confirmation:

```bash
find "$MV_REPO" -maxdepth 2 -mindepth 1 ! -path '*/.intentshell*' | sort
```

## Resetting Between Takes

If you want a fresh recording workspace, rerun only this setup block:

```bash
export RECORD_ROOT="$(mktemp -d /tmp/intentshell-recording.XXXXXX)"
export RM_REPO="$RECORD_ROOT/rm"
export MV_REPO="$RECORD_ROOT/mv"

mkdir "$RM_REPO" "$MV_REPO"
cp -R fixtures/demo_repo/. "$RM_REPO"
cp -R fixtures/demo_repo/. "$MV_REPO"
mkdir "$MV_REPO/archive"
```
