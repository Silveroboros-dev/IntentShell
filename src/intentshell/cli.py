from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import VerificationResult, category_label, verify_command
from .storage import (
    append_audit_record,
    execute_safe_move,
    list_trash_operations,
    move_targets_to_trash,
    read_audit_records,
    restore_operation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intentshell",
        description="Verify that supported rm and mv commands match an explicit intent note.",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    verify_parser = subparsers.add_parser("verify", help="Verify a supported rm or mv command.")
    verify_parser.add_argument("--command", required=True, help="Command to verify.")
    verify_parser.add_argument("--intent", required=True, help="Intent note to enforce.")
    verify_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory used to expand targets and store local state.",
    )
    verify_parser.add_argument(
        "--apply",
        choices=["safe"],
        help="Execute the accepted safe rewrite after verification.",
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of formatted text.",
    )

    trash_parser = subparsers.add_parser("trash", help="Inspect or restore deleted targets.")
    trash_subparsers = trash_parser.add_subparsers(dest="trash_command", required=True)

    list_parser = trash_subparsers.add_parser("list", help="List stored trash operations.")
    list_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory with .intentshell state.",
    )

    restore_parser = trash_subparsers.add_parser("restore", help="Restore a trashed operation.")
    restore_parser.add_argument("operation_id", help="Operation id from `trash list`.")
    restore_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory with .intentshell state.",
    )
    restore_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing paths when restoring.",
    )

    audit_parser = subparsers.add_parser("audit", help="Inspect verification audit records.")
    audit_subparsers = audit_parser.add_subparsers(dest="audit_command", required=True)

    audit_list_parser = audit_subparsers.add_parser("list", help="List recent audit records.")
    audit_list_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory with .intentshell state.",
    )
    audit_list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of records to show, newest first.",
    )

    audit_show_parser = audit_subparsers.add_parser("show", help="Show one audit record.")
    audit_show_parser.add_argument(
        "target",
        nargs="?",
        default="latest",
        help="Use 'latest' or a 1-based index from `audit list`.",
    )
    audit_show_parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory with .intentshell state.",
    )
    audit_show_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON for the selected record.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.subcommand == "verify":
        return _handle_verify(args)
    if args.subcommand == "trash":
        return _handle_trash(args)
    if args.subcommand == "audit":
        return _handle_audit(args)
    parser.error(f"Unknown subcommand: {args.subcommand}")
    return 1


def _handle_verify(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd).resolve()
    result = verify_command(args.command, args.intent, cwd)
    execution: dict[str, object] | None = None

    if args.apply == "safe" and result.parse_error is None and result.safe_targets:
        if result.command_type == "rm":
            operation = move_targets_to_trash(cwd, result, result.safe_targets)
            execution = {
                "status": "trashed",
                "operation": operation.to_dict(),
            }
        elif result.command_type == "mv":
            operation = execute_safe_move(cwd, result, result.safe_targets)
            execution = {
                "status": "moved",
                "operation": operation,
            }
        else:
            raise ValueError(f"Unsupported command type for execution: {result.command_type}")

    audit_path = append_audit_record(cwd, result, execution)

    if args.json:
        payload = {
            "verification": result.to_dict(),
            "execution": execution,
            "audit_log": str(audit_path),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_verification(result, execution, audit_path))

    if result.parse_error:
        return 1
    if execution is None and result.status in {"rewrite_required", "blocked"}:
        return 2
    return 0


def _handle_trash(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd).resolve()
    if args.trash_command == "list":
        operations = list_trash_operations(cwd)
        if not operations:
            print("No trash entries recorded yet.")
            return 0
        for operation in operations:
            targets = ", ".join(operation["stored_targets"])
            restored_at = operation.get("restored_at")
            suffix = f" | restored {restored_at}" if restored_at else ""
            print(f"{operation['operation_id']} | {operation['created_at']} | {targets}{suffix}")
        return 0

    if args.trash_command == "restore":
        restored = restore_operation(cwd, args.operation_id, overwrite=args.overwrite)
        print(
            f"Restored {len(restored['restored_paths'])} path(s) from {restored['operation_id']} at {restored['restored_at']}."
        )
        return 0

    raise ValueError(f"Unknown trash subcommand: {args.trash_command}")


def _handle_audit(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd).resolve()
    audit_path, records = read_audit_records(cwd)

    if args.audit_command == "list":
        if not records:
            print(f"No audit records found at {audit_path}.")
            return 0
        limit = max(args.limit, 1)
        recent_records = list(reversed(records[-limit:]))
        for index, record in enumerate(recent_records, start=1):
            verification = record["verification"]
            print(
                f"{index} | {record['recorded_at']} | "
                f"{verification['command_type']} | {verification['status']} | {verification['command']}"
            )
        return 0

    if args.audit_command == "show":
        if not records:
            print(f"No audit records found at {audit_path}.")
            return 1
        try:
            record = _select_audit_record(records, args.target)
        except ValueError as error:
            print(error)
            return 1

        if args.json:
            print(json.dumps(record, indent=2, sort_keys=True))
        else:
            print(render_audit_record(record, audit_path))
        return 0

    raise ValueError(f"Unknown audit subcommand: {args.audit_command}")


def render_verification(
    result: VerificationResult,
    execution: dict[str, object] | None,
    audit_path: Path,
) -> str:
    lines = [
        f"command type: {result.command_type}",
        f"status: {result.status}",
        f"command: {result.command}",
        f"intent: {result.intent}",
        f"policy: {result.policy_name or 'n/a'}",
    ]

    if result.parse_error:
        lines.append(f"error: {result.parse_error}")
        if result.missing_operands:
            lines.append("missing operands:")
            lines.extend(f"  - {operand}" for operand in result.missing_operands)
        lines.append(f"audit log: {audit_path}")
        return "\n".join(lines)

    allowed = ", ".join(category_label(category) for category in result.allowed_categories)
    lines.append(f"allowed categories: {allowed}")

    lines.append("expanded targets:")
    lines.extend(_format_targets(result.expanded_targets))

    if result.destination is not None:
        destination_label = category_label(result.destination.category)
        destination_kind = result.destination.kind.replace("_", " ")
        lines.append(
            "destination: "
            f"{result.destination.path} [{destination_label}] "
            f"({destination_kind}; {result.destination.reason})"
        )

    if result.violations:
        lines.append("violations:")
        lines.extend(_format_targets(result.violations))
    else:
        lines.append("violations: none")

    if result.safe_rewrite:
        lines.append(f"safe rewrite: {result.safe_rewrite}")
    else:
        lines.append("safe rewrite: none")

    if execution is not None:
        operation = execution["operation"]
        if execution["status"] == "trashed":
            lines.append(
                f"executed: moved {len(operation['stored_targets'])} path(s) to local trash as {operation['operation_id']}"
            )
        elif execution["status"] == "moved":
            lines.append(
                f"executed: moved {len(operation['moved_targets'])} path(s) into {operation['destination']}"
            )

    lines.append(f"audit log: {audit_path}")
    return "\n".join(lines)


def render_audit_record(record: dict[str, object], audit_path: Path) -> str:
    verification = record["verification"]
    lines = [
        f"recorded at: {record['recorded_at']}",
        f"command type: {verification['command_type']}",
        f"status: {verification['status']}",
        f"command: {verification['command']}",
        f"intent: {verification['intent']}",
        f"policy: {verification['policy_name'] or 'n/a'}",
    ]

    if verification["parse_error"]:
        lines.append(f"error: {verification['parse_error']}")
    else:
        allowed = ", ".join(
            category_label(category) for category in verification["allowed_categories"]
        )
        lines.append(f"allowed categories: {allowed}")
        lines.append("expanded targets:")
        lines.extend(_format_target_dicts(verification["expanded_targets"]))

        destination = verification.get("destination")
        if destination is not None:
            destination_label = category_label(destination["category"])
            destination_kind = destination["kind"].replace("_", " ")
            lines.append(
                "destination: "
                f"{destination['path']} [{destination_label}] "
                f"({destination_kind}; {destination['reason']})"
            )

        violations = verification["violations"]
        if violations:
            lines.append("violations:")
            lines.extend(_format_target_dicts(violations))
        else:
            lines.append("violations: none")

        lines.append(f"safe rewrite: {verification['safe_rewrite'] or 'none'}")

    execution = record.get("execution")
    if execution is not None:
        operation = execution["operation"]
        if execution["status"] == "trashed":
            lines.append(
                f"execution: moved {len(operation['stored_targets'])} path(s) to local trash as {operation['operation_id']}"
            )
        elif execution["status"] == "moved":
            lines.append(
                f"execution: moved {len(operation['moved_targets'])} path(s) into {operation['destination']}"
            )

    lines.append(f"audit log: {audit_path}")
    return "\n".join(lines)


def _format_targets(targets: list) -> list[str]:
    return [
        f"  - {target.path} [{category_label(target.category)}] ({target.reason})"
        for target in targets
    ]


def _format_target_dicts(targets: list[dict[str, str]]) -> list[str]:
    return [
        f"  - {target['path']} [{category_label(target['category'])}] ({target['reason']})"
        for target in targets
    ]


def _select_audit_record(records: list[dict[str, object]], target: str) -> dict[str, object]:
    if target == "latest":
        return records[-1]

    try:
        index = int(target)
    except ValueError as error:
        raise ValueError("Audit target must be 'latest' or a positive integer.") from error

    if index < 1:
        raise ValueError("Audit target index must be 1 or greater.")

    reversed_records = list(reversed(records))
    if index > len(reversed_records):
        raise ValueError(f"Audit target index {index} is out of range; only {len(reversed_records)} record(s) exist.")
    return reversed_records[index - 1]
