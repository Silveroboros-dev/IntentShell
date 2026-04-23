from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from intentshell.cli import main
from intentshell.core import verify_command
from intentshell.storage import list_trash_operations, move_targets_to_trash, restore_operation


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "demo_repo"


def copy_fixture_repo(destination_root: Path) -> Path:
    repo_path = destination_root / "demo_repo"
    shutil.copytree(FIXTURE_ROOT, repo_path, ignore=shutil.ignore_patterns(".intentshell"))
    return repo_path


class IntentShellTests(unittest.TestCase):
    def test_broad_rm_requires_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("rm -rf ./*", "delete only build artifacts", repo_path)

            self.assertEqual(result.status, "rewrite_required")
            self.assertEqual(
                [target.path for target in result.expanded_targets],
                ["build", "dist", "coverage", "src", "config", "README.md"],
            )
            self.assertEqual(
                [target.path for target in result.violations],
                ["src", "config", "README.md"],
            )
            self.assertEqual(
                [target.path for target in result.safe_targets],
                ["build", "dist", "coverage"],
            )
            self.assertEqual(result.safe_rewrite, "rm -rf build dist coverage")

    def test_safe_targets_can_round_trip_through_local_trash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("rm -rf ./*", "delete only build artifacts", repo_path)

            operation = move_targets_to_trash(repo_path, result, result.safe_targets)
            self.assertFalse((repo_path / "build").exists())
            self.assertFalse((repo_path / "dist").exists())
            self.assertFalse((repo_path / "coverage").exists())
            self.assertTrue((repo_path / "src").exists())

            trash_entries = list_trash_operations(repo_path)
            self.assertEqual(len(trash_entries), 1)
            self.assertEqual(trash_entries[0]["operation_id"], operation.operation_id)

            restored = restore_operation(repo_path, operation.operation_id)
            self.assertEqual(
                restored["restored_paths"],
                ["build", "dist", "coverage"],
            )
            self.assertTrue((repo_path / "build").exists())
            self.assertTrue((repo_path / "dist").exists())
            self.assertTrue((repo_path / "coverage").exists())

    def test_readme_is_classified_as_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("rm -rf README.md", "delete only build artifacts", repo_path)

            self.assertEqual(result.status, "blocked")
            self.assertEqual(len(result.violations), 1)
            self.assertEqual(result.violations[0].path, "README.md")
            self.assertEqual(result.violations[0].category, "documentation")

    def test_cli_json_output_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "verify",
                        "--cwd",
                        str(repo_path),
                        "--command",
                        "rm -rf ./*",
                        "--intent",
                        "delete only build artifacts",
                        "--json",
                    ]
                )

            self.assertEqual(exit_code, 2)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["verification"]["status"], "rewrite_required")
            self.assertEqual(
                payload["verification"]["safe_rewrite"],
                "rm -rf build dist coverage",
            )

    def test_trash_list_accepts_cwd_after_nested_subcommand(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("rm -rf ./*", "delete only build artifacts", repo_path)
            operation = move_targets_to_trash(repo_path, result, result.safe_targets)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trash", "list", "--cwd", str(repo_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn(operation.operation_id, stdout.getvalue())

    def test_apply_safe_still_fails_when_no_safe_targets_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "verify",
                        "--cwd",
                        str(repo_path),
                        "--command",
                        "rm -rf src config",
                        "--intent",
                        "delete only build artifacts",
                        "--apply",
                        "safe",
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("safe rewrite: none", stdout.getvalue())

    def test_mv_requires_rewrite_for_mixed_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            (repo_path / "archive").mkdir()

            result = verify_command("mv build src archive", "move only build artifacts", repo_path)

            self.assertEqual(result.command_type, "mv")
            self.assertEqual(result.status, "rewrite_required")
            self.assertEqual(
                [target.path for target in result.expanded_targets],
                ["build", "src"],
            )
            self.assertEqual(
                [target.path for target in result.violations],
                ["src"],
            )
            self.assertEqual(
                [target.path for target in result.safe_targets],
                ["build"],
            )
            self.assertEqual(result.safe_rewrite, "mv build archive")
            self.assertIsNotNone(result.destination)
            self.assertEqual(result.destination.path, "archive")
            self.assertEqual(result.destination.kind, "existing_directory")

    def test_mv_apply_safe_moves_only_allowed_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            (repo_path / "archive").mkdir()
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "verify",
                        "--cwd",
                        str(repo_path),
                        "--command",
                        "mv build src archive",
                        "--intent",
                        "move only build artifacts",
                        "--apply",
                        "safe",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertFalse((repo_path / "build").exists())
            self.assertTrue((repo_path / "archive" / "build").exists())
            self.assertTrue((repo_path / "src").exists())
            self.assertIn("executed: moved 1 path(s) into archive", stdout.getvalue())

    def test_mv_blocks_destinations_outside_the_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("mv build ../archive", "move only build artifacts", repo_path)

            self.assertEqual(result.status, "error")
            self.assertIn("destinations inside the current working directory", result.parse_error)

    def test_mv_blocks_overwrite_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            (repo_path / "archive").mkdir()
            shutil.copytree(repo_path / "build", repo_path / "archive" / "build")

            result = verify_command("mv build archive", "move only build artifacts", repo_path)

            self.assertEqual(result.status, "error")
            self.assertIn("overwrite existing path 'archive/build'", result.parse_error)

    def test_unsupported_destructive_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            result = verify_command("rmdir build", "delete only build artifacts", repo_path)

            self.assertEqual(result.status, "error")
            self.assertIn("supports rm and mv commands only", result.parse_error)

    def test_audit_list_and_show_latest_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                main(
                    [
                        "verify",
                        "--cwd",
                        str(repo_path),
                        "--command",
                        "rm -rf ./*",
                        "--intent",
                        "delete only build artifacts",
                    ]
                )

            list_stdout = io.StringIO()
            with redirect_stdout(list_stdout):
                exit_code = main(["audit", "list", "--cwd", str(repo_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("rm | rewrite_required | rm -rf ./*", list_stdout.getvalue())

            show_stdout = io.StringIO()
            with redirect_stdout(show_stdout):
                exit_code = main(["audit", "show", "latest", "--cwd", str(repo_path)])

            self.assertEqual(exit_code, 0)
            self.assertIn("recorded at:", show_stdout.getvalue())
            self.assertIn("safe rewrite: rm -rf build dist coverage", show_stdout.getvalue())

    def test_audit_show_json_returns_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = copy_fixture_repo(Path(tmpdir))
            with redirect_stdout(io.StringIO()):
                main(
                    [
                        "verify",
                        "--cwd",
                        str(repo_path),
                        "--command",
                        "mv build dist archive",
                        "--intent",
                        "move only build artifacts",
                    ]
                )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["audit", "show", "latest", "--cwd", str(repo_path), "--json"])

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["verification"]["command_type"], "mv")
            self.assertEqual(payload["verification"]["status"], "error")
