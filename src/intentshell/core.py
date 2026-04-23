from __future__ import annotations

import glob
import re
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath


ARTIFACT_NAMES = {
    "build",
    "dist",
    "coverage",
    "out",
    "target",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".parcel-cache",
    ".turbo",
    ".cache",
    "__pycache__",
}
ARTIFACT_SUFFIXES = (".pyc", ".pyo", ".o", ".obj", ".tmp", ".cache")
LOG_NAMES = {"log", "logs"}
LOG_SUFFIXES = (".log",)
DOCUMENTATION_DIRS = {"docs", "doc"}
DOCUMENTATION_NAMES = {
    "readme",
    "readme.md",
    "license",
    "license.md",
    "changelog",
    "changelog.md",
    "contributing",
    "contributing.md",
}
DOCUMENTATION_SUFFIXES = (".md",)
SOURCE_DIRS = {"src", "app", "lib", "components", "pages", "server", "client", "tests"}
SOURCE_SUFFIXES = (
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
)
CONFIG_DIRS = {"config", "configs", ".github", ".vscode"}
CONFIG_NAMES = {
    "makefile",
    "dockerfile",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "docker-compose.yml",
    "docker-compose.yaml",
}
CONFIG_SUFFIXES = (".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".lock")
SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_ed25519",
    "credentials",
}
SECRET_SUFFIXES = (".pem", ".key", ".crt", ".p12", ".pfx")
USER_DATA_SUFFIXES = (
    ".txt",
    ".rtf",
    ".doc",
    ".docx",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".csv",
    ".tsv",
)

CATEGORY_LABELS = {
    "generated_artifact": "generated artifact",
    "logs": "logs",
    "source": "source code",
    "config": "configuration",
    "documentation": "documentation",
    "secret": "secret",
    "user_data": "user data",
    "unknown": "unknown",
}

INTENT_ALIASES = {
    "build artifacts": ("generated_artifact",),
    "generated artifacts": ("generated_artifact",),
    "artifacts": ("generated_artifact",),
    "temporary files": ("generated_artifact",),
    "temp files": ("generated_artifact",),
    "logs": ("logs",),
    "log files": ("logs",),
    "source": ("source",),
    "source code": ("source",),
    "source files": ("source",),
    "config": ("config",),
    "configuration": ("config",),
    "config files": ("config",),
    "configuration files": ("config",),
    "documentation": ("documentation",),
    "documentation files": ("documentation",),
    "secrets": ("secret",),
    "secret files": ("secret",),
    "user data": ("user_data",),
    "docs": ("documentation",),
}

CATEGORY_PRIORITY = {
    "generated_artifact": 0,
    "source": 1,
    "config": 2,
    "documentation": 3,
    "logs": 4,
    "secret": 5,
    "user_data": 6,
    "unknown": 7,
}
ARTIFACT_PRIORITY = {
    "build": 0,
    "dist": 1,
    "coverage": 2,
}
INTENT_PREFIXES = {
    "delete": ("delete only ", "remove only "),
    "move": ("move only ",),
}


@dataclass(frozen=True)
class ParsedRmCommand:
    raw: str
    flags: tuple[str, ...]
    recursive: bool
    force: bool
    verbose: bool
    operands: tuple[str, ...]


@dataclass(frozen=True)
class ParsedMvCommand:
    raw: str
    flags: tuple[str, ...]
    verbose: bool
    source_operands: tuple[str, ...]
    destination_operand: str


@dataclass(frozen=True)
class IntentPolicy:
    raw: str
    action: str
    policy_name: str
    allowed_categories: tuple[str, ...]


@dataclass(frozen=True)
class ClassifiedTarget:
    path: str
    category: str
    reason: str


@dataclass
class DestinationDetails:
    path: str
    kind: str
    category: str
    reason: str


@dataclass
class VerificationResult:
    command_type: str
    command: str
    intent: str
    working_directory: str
    status: str
    policy_name: str | None
    allowed_categories: list[str]
    expanded_targets: list[ClassifiedTarget]
    violations: list[ClassifiedTarget]
    safe_targets: list[ClassifiedTarget]
    safe_rewrite: str | None
    destination: DestinationDetails | None
    missing_operands: list[str]
    parse_error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "command_type": self.command_type,
            "command": self.command,
            "intent": self.intent,
            "working_directory": self.working_directory,
            "status": self.status,
            "policy_name": self.policy_name,
            "allowed_categories": self.allowed_categories,
            "expanded_targets": [asdict(item) for item in self.expanded_targets],
            "violations": [asdict(item) for item in self.violations],
            "safe_targets": [asdict(item) for item in self.safe_targets],
            "safe_rewrite": self.safe_rewrite,
            "destination": asdict(self.destination) if self.destination is not None else None,
            "missing_operands": self.missing_operands,
            "parse_error": self.parse_error,
        }


def verify_command(command: str, intent: str, working_directory: str | Path = ".") -> VerificationResult:
    cwd = Path(working_directory).resolve()
    command_type = _peek_command_name(command) or "unknown"
    try:
        if command_type == "rm":
            parsed = parse_rm_command(command)
            policy = parse_intent_policy(intent, expected_action="delete")
            return _verify_rm_command(parsed, policy, cwd)
        if command_type == "mv":
            parsed = parse_mv_command(command)
            policy = parse_intent_policy(intent, expected_action="move")
            return _verify_mv_command(parsed, policy, cwd)
        raise ValueError("This MVP currently supports rm and mv commands only.")
    except ValueError as error:
        return VerificationResult(
            command_type=command_type,
            command=command,
            intent=intent,
            working_directory=str(cwd),
            status="error",
            policy_name=None,
            allowed_categories=[],
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=[],
            parse_error=str(error),
        )


def _verify_rm_command(
    parsed: ParsedRmCommand,
    policy: IntentPolicy,
    cwd: Path,
) -> VerificationResult:
    expanded_paths, missing_operands = expand_operands(parsed.operands, cwd)
    if missing_operands and not parsed.force:
        return VerificationResult(
            command_type="rm",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error=(
                "Command references paths that do not exist: "
                + ", ".join(sorted(missing_operands))
            ),
        )

    if not expanded_paths:
        return VerificationResult(
            command_type="rm",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error="Command did not expand to any targets.",
        )

    if any(not _is_relative_to(path, cwd) for path in expanded_paths):
        return VerificationResult(
            command_type="rm",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error="This MVP only supports targets inside the current working directory.",
        )

    if any(path.is_dir() for path in expanded_paths) and not parsed.recursive:
        return VerificationResult(
            command_type="rm",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error="Command targets directories but is missing -r or -R.",
        )

    classified_targets = order_targets(
        [classify_target(path, cwd) for path in expanded_paths]
    )
    safe_targets = [
        target for target in classified_targets if target.category in policy.allowed_categories
    ]
    violations = [
        target for target in classified_targets if target.category not in policy.allowed_categories
    ]

    if violations and safe_targets:
        status = "rewrite_required"
    elif violations:
        status = "blocked"
    else:
        status = "accepted"

    return VerificationResult(
        command_type="rm",
        command=parsed.raw,
        intent=policy.raw,
        working_directory=str(cwd),
        status=status,
        policy_name=policy.policy_name,
        allowed_categories=list(policy.allowed_categories),
        expanded_targets=classified_targets,
        violations=violations,
        safe_targets=safe_targets,
        safe_rewrite=synthesize_rm_rewrite(parsed, safe_targets),
        destination=None,
        missing_operands=missing_operands,
        parse_error=None,
    )


def _verify_mv_command(
    parsed: ParsedMvCommand,
    policy: IntentPolicy,
    cwd: Path,
) -> VerificationResult:
    expanded_paths, missing_operands = expand_operands(parsed.source_operands, cwd)
    if missing_operands:
        return VerificationResult(
            command_type="mv",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error=(
                "Command references sources that do not exist: "
                + ", ".join(sorted(missing_operands))
            ),
        )

    if not expanded_paths:
        return VerificationResult(
            command_type="mv",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error="Command did not expand to any source targets.",
        )

    if any(not _is_relative_to(path, cwd) for path in expanded_paths):
        return VerificationResult(
            command_type="mv",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error="This MVP only supports sources inside the current working directory.",
        )

    try:
        destination, destination_path, destination_is_directory = prepare_mv_destination(
            parsed,
            expanded_paths,
            cwd,
        )
        validate_move_plan(expanded_paths, destination_path, destination_is_directory, cwd)
    except ValueError as error:
        return VerificationResult(
            command_type="mv",
            command=parsed.raw,
            intent=policy.raw,
            working_directory=str(cwd),
            status="error",
            policy_name=policy.policy_name,
            allowed_categories=list(policy.allowed_categories),
            expanded_targets=[],
            violations=[],
            safe_targets=[],
            safe_rewrite=None,
            destination=None,
            missing_operands=missing_operands,
            parse_error=str(error),
        )

    classified_targets = order_targets(
        [classify_target(path, cwd) for path in expanded_paths]
    )
    safe_targets = [
        target for target in classified_targets if target.category in policy.allowed_categories
    ]
    violations = [
        target for target in classified_targets if target.category not in policy.allowed_categories
    ]

    if violations and safe_targets:
        status = "rewrite_required"
    elif violations:
        status = "blocked"
    else:
        status = "accepted"

    return VerificationResult(
        command_type="mv",
        command=parsed.raw,
        intent=policy.raw,
        working_directory=str(cwd),
        status=status,
        policy_name=policy.policy_name,
        allowed_categories=list(policy.allowed_categories),
        expanded_targets=classified_targets,
        violations=violations,
        safe_targets=safe_targets,
        safe_rewrite=synthesize_mv_rewrite(parsed, safe_targets),
        destination=destination,
        missing_operands=missing_operands,
        parse_error=None,
    )


def parse_rm_command(command: str) -> ParsedRmCommand:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as error:
        raise ValueError(f"Could not parse command: {error}") from error

    if not tokens:
        raise ValueError("Command is empty.")
    if tokens[0] != "rm":
        raise ValueError("This MVP currently supports rm commands only.")

    recursive = False
    force = False
    verbose = False
    flags: list[str] = []
    operands: list[str] = []
    parsing_options = True

    for token in tokens[1:]:
        if parsing_options and token == "--":
            parsing_options = False
            continue
        if parsing_options and token.startswith("--"):
            if token == "--recursive":
                recursive = True
                flags.append(token)
                continue
            if token == "--force":
                force = True
                flags.append(token)
                continue
            if token == "--verbose":
                verbose = True
                flags.append(token)
                continue
            raise ValueError(f"Unsupported rm option: {token}")
        if parsing_options and token.startswith("-") and token != "-":
            for flag in token[1:]:
                if flag in {"r", "R"}:
                    recursive = True
                elif flag == "f":
                    force = True
                elif flag == "v":
                    verbose = True
                else:
                    raise ValueError(f"Unsupported rm option: -{flag}")
            flags.append(token)
            continue
        parsing_options = False
        operands.append(token)

    if not operands:
        raise ValueError("rm command must include at least one path or glob.")

    return ParsedRmCommand(
        raw=command,
        flags=tuple(flags),
        recursive=recursive,
        force=force,
        verbose=verbose,
        operands=tuple(operands),
    )


def parse_mv_command(command: str) -> ParsedMvCommand:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as error:
        raise ValueError(f"Could not parse command: {error}") from error

    if not tokens:
        raise ValueError("Command is empty.")
    if tokens[0] != "mv":
        raise ValueError("parse_mv_command expects an mv command.")

    verbose = False
    flags: list[str] = []
    operands: list[str] = []
    parsing_options = True

    for token in tokens[1:]:
        if parsing_options and token == "--":
            parsing_options = False
            continue
        if parsing_options and token.startswith("--"):
            if token == "--verbose":
                verbose = True
                flags.append(token)
                continue
            raise ValueError(f"Unsupported mv option: {token}")
        if parsing_options and token.startswith("-") and token != "-":
            for flag in token[1:]:
                if flag == "v":
                    verbose = True
                else:
                    raise ValueError(f"Unsupported mv option: -{flag}")
            flags.append(token)
            continue
        parsing_options = False
        operands.append(token)

    if len(operands) < 2:
        raise ValueError("mv command must include at least one source and one destination.")

    return ParsedMvCommand(
        raw=command,
        flags=tuple(flags),
        verbose=verbose,
        source_operands=tuple(operands[:-1]),
        destination_operand=operands[-1],
    )


def parse_intent_policy(intent: str, expected_action: str | None = None) -> IntentPolicy:
    normalized = re.sub(r"[^a-z0-9,\s]+", " ", intent.lower()).strip()
    action = None
    body = None
    for candidate_action, prefixes in INTENT_PREFIXES.items():
        for prefix in prefixes:
            if normalized.startswith(prefix):
                action = candidate_action
                body = normalized[len(prefix) :].strip()
                break
        if body is not None:
            break
    if not body:
        raise ValueError("Intent must start with 'delete only', 'remove only', or 'move only'.")
    if expected_action is not None and action != expected_action:
        expected_prefixes = " or ".join(
            f"'{prefix.strip()}'" for prefix in INTENT_PREFIXES[expected_action]
        )
        raise ValueError(f"Intent for this command must start with {expected_prefixes}.")

    phrases = [
        phrase.strip()
        for phrase in re.split(r",|\band\b", body)
        if phrase.strip()
    ]
    if not phrases:
        raise ValueError("Intent did not name any supported category.")

    allowed_categories: list[str] = []
    for phrase in phrases:
        aliases = INTENT_ALIASES.get(phrase)
        if aliases is None:
            supported = ", ".join(sorted(INTENT_ALIASES))
            raise ValueError(
                f"Unsupported intent phrase '{phrase}'. Supported phrases: {supported}"
            )
        allowed_categories.extend(aliases)

    deduped = tuple(dict.fromkeys(allowed_categories))
    policy_name = f"{action}:" + ",".join(deduped)
    return IntentPolicy(raw=intent, action=action, policy_name=policy_name, allowed_categories=deduped)


def expand_operands(operands: tuple[str, ...], cwd: Path) -> tuple[list[Path], list[str]]:
    expanded: list[Path] = []
    missing: list[str] = []
    seen: set[Path] = set()

    for operand in operands:
        matches = _expand_operand(operand, cwd)
        if not matches:
            missing.append(operand)
            continue
        for match in matches:
            resolved = match.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            expanded.append(resolved)

    return expanded, missing


def prepare_mv_destination(
    parsed: ParsedMvCommand,
    expanded_paths: list[Path],
    cwd: Path,
) -> tuple[DestinationDetails, Path, bool]:
    if _looks_like_glob(parsed.destination_operand):
        raise ValueError("mv destination may not contain globs in this MVP.")

    destination_path = _resolve_candidate_path(parsed.destination_operand, cwd)
    if not _is_relative_to(destination_path, cwd):
        raise ValueError("This MVP only supports destinations inside the current working directory.")

    if len(expanded_paths) > 1:
        if not destination_path.exists() or not destination_path.is_dir():
            raise ValueError("mv with multiple sources requires an existing destination directory.")
        destination_is_directory = True
        kind = "existing_directory"
    else:
        if destination_path.exists() and destination_path.is_dir():
            destination_is_directory = True
            kind = "existing_directory"
        else:
            if not destination_path.parent.exists():
                raise ValueError("Destination parent directory does not exist.")
            destination_is_directory = False
            kind = "existing_path" if destination_path.exists() else "new_path"

    classified = classify_target(destination_path, cwd)
    destination = DestinationDetails(
        path=classified.path,
        kind=kind,
        category=classified.category,
        reason=classified.reason,
    )
    return destination, destination_path, destination_is_directory


def validate_move_plan(
    source_paths: list[Path],
    destination_path: Path,
    destination_is_directory: bool,
    cwd: Path,
) -> None:
    for source_path in source_paths:
        final_destination = (
            destination_path / source_path.name if destination_is_directory else destination_path
        ).resolve()

        if source_path.resolve() == final_destination:
            relative_source = _display_path(source_path, cwd)
            raise ValueError(f"Source and destination resolve to the same path: {relative_source}")

        if source_path.is_dir() and _is_relative_to(final_destination, source_path.resolve()):
            relative_source = _display_path(source_path, cwd)
            relative_destination = _display_path(final_destination, cwd)
            raise ValueError(
                f"Cannot move directory '{relative_source}' into its own descendant '{relative_destination}'."
            )

        if final_destination.exists():
            relative_destination = _display_path(final_destination, cwd)
            raise ValueError(
                f"mv would overwrite existing path '{relative_destination}'. Overwrite semantics are not yet supported in this MVP."
            )


def classify_target(path: Path, cwd: Path) -> ClassifiedTarget:
    try:
        rel_path = path.relative_to(cwd).as_posix()
    except ValueError:
        rel_path = path.as_posix()

    parts = [part.lower() for part in PurePosixPath(rel_path).parts]
    name = path.name.lower()

    if name in SECRET_NAMES or any(name.endswith(suffix) for suffix in SECRET_SUFFIXES):
        return ClassifiedTarget(rel_path, "secret", "matches a secret filename pattern")

    if "secrets" in parts or "secret" in parts:
        return ClassifiedTarget(rel_path, "secret", "lives in a secrets path")

    if name in ARTIFACT_NAMES or any(part in ARTIFACT_NAMES for part in parts):
        return ClassifiedTarget(
            rel_path, "generated_artifact", "matches a generated-artifact directory name"
        )

    if any(name.endswith(suffix) for suffix in ARTIFACT_SUFFIXES):
        return ClassifiedTarget(
            rel_path, "generated_artifact", "matches a generated-artifact file suffix"
        )

    if name in SOURCE_DIRS or any(part in SOURCE_DIRS for part in parts[:-1]):
        return ClassifiedTarget(rel_path, "source", "lives in a source directory")

    if any(name.endswith(suffix) for suffix in SOURCE_SUFFIXES):
        return ClassifiedTarget(rel_path, "source", "matches a source file suffix")

    if name in CONFIG_NAMES or any(part in CONFIG_DIRS for part in parts):
        return ClassifiedTarget(rel_path, "config", "matches a config path pattern")

    if any(name.endswith(suffix) for suffix in CONFIG_SUFFIXES):
        return ClassifiedTarget(rel_path, "config", "matches a config file suffix")

    if (
        name in DOCUMENTATION_NAMES
        or any(part in DOCUMENTATION_DIRS for part in parts[:-1])
        or any(name.endswith(suffix) for suffix in DOCUMENTATION_SUFFIXES)
    ):
        return ClassifiedTarget(rel_path, "documentation", "looks like project documentation")

    if name in LOG_NAMES or any(part in LOG_NAMES for part in parts):
        return ClassifiedTarget(rel_path, "logs", "matches a log directory name")

    if any(name.endswith(suffix) for suffix in LOG_SUFFIXES):
        return ClassifiedTarget(rel_path, "logs", "matches a log file suffix")

    if any(name.endswith(suffix) for suffix in USER_DATA_SUFFIXES):
        return ClassifiedTarget(rel_path, "user_data", "matches a user-data file suffix")

    return ClassifiedTarget(rel_path, "unknown", "did not match an explicit policy category")


def synthesize_rm_rewrite(
    parsed: ParsedRmCommand,
    safe_targets: list[ClassifiedTarget],
) -> str | None:
    if not safe_targets:
        return None

    options = []
    if parsed.recursive:
        options.append("r")
    if parsed.force:
        options.append("f")
    if parsed.verbose:
        options.append("v")
    flag_text = f" -{''.join(options)}" if options else ""
    targets = " ".join(shlex.quote(target.path) for target in safe_targets)
    return f"rm{flag_text} {targets}"


def synthesize_mv_rewrite(
    parsed: ParsedMvCommand,
    safe_targets: list[ClassifiedTarget],
) -> str | None:
    if not safe_targets:
        return None

    options = []
    if parsed.verbose:
        options.append("v")
    flag_text = f" -{''.join(options)}" if options else ""
    targets = " ".join(shlex.quote(target.path) for target in safe_targets)
    destination = shlex.quote(parsed.destination_operand)
    return f"mv{flag_text} {targets} {destination}"


def order_targets(targets: list[ClassifiedTarget]) -> list[ClassifiedTarget]:
    return sorted(targets, key=_target_sort_key)


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def _expand_operand(operand: str, cwd: Path) -> list[Path]:
    if _looks_like_glob(operand):
        pattern = str(cwd / operand)
        return [Path(match) for match in sorted(glob.glob(pattern, recursive=True))]

    candidate = _resolve_candidate_path(operand, cwd)
    if candidate.exists():
        return [candidate]
    return []


def _looks_like_glob(value: str) -> bool:
    return any(char in value for char in "*?[]")


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def _target_sort_key(target: ClassifiedTarget) -> tuple[int, int, str]:
    category_rank = CATEGORY_PRIORITY.get(target.category, 99)
    name = PurePosixPath(target.path).name.lower()
    artifact_rank = ARTIFACT_PRIORITY.get(name, 99)
    return category_rank, artifact_rank, target.path


def _peek_command_name(command: str) -> str | None:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return None
    if not tokens:
        return None
    return tokens[0]


def _resolve_candidate_path(operand: str, cwd: Path) -> Path:
    candidate = Path(operand)
    if not candidate.is_absolute():
        candidate = cwd / candidate
    return candidate.resolve()


def _display_path(path: Path, cwd: Path) -> str:
    try:
        return path.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
