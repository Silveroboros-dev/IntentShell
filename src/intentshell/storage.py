from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .core import ClassifiedTarget, VerificationResult


STATE_DIR = ".intentshell"
TRASH_DIR = "trash"
AUDIT_FILE = "audit.jsonl"
MANIFEST_FILE = "manifest.json"


@dataclass(frozen=True)
class TrashOperation:
    operation_id: str
    operation_dir: Path
    created_at: str
    stored_targets: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "created_at": self.created_at,
            "stored_targets": self.stored_targets,
            "operation_dir": str(self.operation_dir),
        }


def append_audit_record(
    working_directory: str | Path,
    result: VerificationResult,
    execution: dict[str, object] | None = None,
) -> Path:
    cwd = Path(working_directory).resolve()
    state_dir = _ensure_state_dir(cwd)
    audit_path = state_dir / AUDIT_FILE
    record = {
        "recorded_at": _timestamp(),
        "verification": result.to_dict(),
        "execution": execution,
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")
    return audit_path


def move_targets_to_trash(
    working_directory: str | Path,
    result: VerificationResult,
    targets: list[ClassifiedTarget],
) -> TrashOperation:
    cwd = Path(working_directory).resolve()
    state_dir = _ensure_state_dir(cwd)
    trash_root = state_dir / TRASH_DIR
    operation_id = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    operation_dir = trash_root / operation_id
    payload_dir = operation_dir / "files"
    payload_dir.mkdir(parents=True, exist_ok=False)

    stored_targets: list[str] = []
    for target in targets:
        source_path = cwd / target.path
        destination_path = payload_dir / target.path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(destination_path))
        stored_targets.append(target.path)

    manifest = {
        "operation_id": operation_id,
        "created_at": _timestamp(),
        "original_command": result.command,
        "executed_command": result.safe_rewrite,
        "intent": result.intent,
        "stored_targets": stored_targets,
    }
    with (operation_dir / MANIFEST_FILE).open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return TrashOperation(
        operation_id=operation_id,
        operation_dir=operation_dir,
        created_at=manifest["created_at"],
        stored_targets=stored_targets,
    )


def execute_safe_move(
    working_directory: str | Path,
    result: VerificationResult,
    targets: list[ClassifiedTarget],
) -> dict[str, object]:
    cwd = Path(working_directory).resolve()
    if result.destination is None:
        raise ValueError("Move execution requires a verified destination.")

    destination_root = cwd / result.destination.path
    destination_is_directory = result.destination.kind == "existing_directory"
    moved_targets: list[dict[str, str]] = []

    for target in targets:
        source_path = cwd / target.path
        destination_path = (
            destination_root / source_path.name if destination_is_directory else destination_root
        )
        if not source_path.exists():
            raise FileNotFoundError(f"Verified source '{target.path}' no longer exists.")
        if destination_path.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing destination '{_display_path(destination_path, cwd)}'."
            )
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(destination_path))
        moved_targets.append(
            {
                "source": target.path,
                "destination": _display_path(destination_path, cwd),
            }
        )

    return {
        "destination": result.destination.path,
        "destination_kind": result.destination.kind,
        "moved_targets": moved_targets,
    }


def list_trash_operations(working_directory: str | Path) -> list[dict[str, object]]:
    cwd = Path(working_directory).resolve()
    trash_root = cwd / STATE_DIR / TRASH_DIR
    if not trash_root.exists():
        return []

    operations: list[dict[str, object]] = []
    for manifest_path in sorted(trash_root.glob(f"*/{MANIFEST_FILE}"), reverse=True):
        with manifest_path.open("r", encoding="utf-8") as handle:
            operations.append(json.load(handle))
    return operations


def read_audit_records(working_directory: str | Path) -> tuple[Path, list[dict[str, object]]]:
    cwd = Path(working_directory).resolve()
    audit_path = cwd / STATE_DIR / AUDIT_FILE
    if not audit_path.exists():
        return audit_path, []

    records: list[dict[str, object]] = []
    with audit_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return audit_path, records


def restore_operation(
    working_directory: str | Path,
    operation_id: str,
    overwrite: bool = False,
) -> dict[str, object]:
    cwd = Path(working_directory).resolve()
    operation_dir = cwd / STATE_DIR / TRASH_DIR / operation_id
    manifest_path = operation_dir / MANIFEST_FILE
    payload_dir = operation_dir / "files"

    if not manifest_path.exists():
        raise FileNotFoundError(f"No trash entry found for operation '{operation_id}'.")

    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    restored_paths: list[str] = []
    for relative_path in manifest["stored_targets"]:
        source_path = payload_dir / relative_path
        destination_path = cwd / relative_path
        if destination_path.exists() and not overwrite:
            raise FileExistsError(
                f"Refusing to restore over existing path '{relative_path}'. Use --overwrite to replace it."
            )
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if overwrite and destination_path.exists():
            if destination_path.is_dir():
                shutil.rmtree(destination_path)
            else:
                destination_path.unlink()
        shutil.move(str(source_path), str(destination_path))
        restored_paths.append(relative_path)

    manifest["restored_at"] = _timestamp()
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "operation_id": operation_id,
        "restored_paths": restored_paths,
        "restored_at": manifest["restored_at"],
    }


def _ensure_state_dir(cwd: Path) -> Path:
    state_dir = cwd / STATE_DIR
    (state_dir / TRASH_DIR).mkdir(parents=True, exist_ok=True)
    return state_dir


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _display_path(path: Path, cwd: Path) -> str:
    try:
        return path.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
