from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UnifiedCliTests(unittest.TestCase):
    def _run_root(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "tdx.py", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def _run_scripts_wrapper(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/tdx.py", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_top_level_help_lists_core_commands(self) -> None:
        result = self._run_root("--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("通达信基础接口统一命令入口", result.stdout)
        self.assertIn("get-market-data", result.stdout)
        self.assertIn("setup-tdx-path", result.stdout)
        self.assertIn("python tdx.py <command> [args]", result.stdout)

    def test_command_help_delegates_to_underlying_script(self) -> None:
        result = self._run_root("get-market-data", "--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("获取K线行情数据", result.stdout)
        self.assertIn("--dividend_type {none,front,back}", result.stdout)

    def test_unknown_command_returns_error(self) -> None:
        result = self._run_root("not-a-command")

        self.assertEqual(result.returncode, 2)
        self.assertIn("未知命令: not-a-command", result.stderr)

    def test_scripts_wrapper_keeps_compatibility_label(self) -> None:
        result = self._run_scripts_wrapper("--help")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("python scripts/tdx.py <command> [args]", result.stdout)


if __name__ == "__main__":
    unittest.main()
