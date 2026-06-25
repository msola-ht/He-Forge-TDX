from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]

PERIOD_CHOICES_TEXT = "{1m,5m,15m,30m,1h,1d,1w,1mon,1q,1y,tick}"


class CliHelpTests(unittest.TestCase):
    def _run_help(self, relative_script_path: str) -> str:
        result = subprocess.run(
            [sys.executable, relative_script_path, "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"{relative_script_path} --help exited with {result.returncode}: {result.stderr}",
        )
        self.assertIn("show this help message and exit", result.stdout)
        return result.stdout

    def test_help_for_string_dividend_type_scripts(self) -> None:
        cases = [
            ("scripts/setup_tdx_path.py", ["--output {raw,json,table}"]),
            ("scripts/print_to_tdx.py", ["--output {raw,json,table}"]),
            ("scripts/get_market_data.py", ["--period", PERIOD_CHOICES_TEXT, "--dividend_type {none,front,back}"]),
            ("scripts/subscribe_quote.py", ["--period", PERIOD_CHOICES_TEXT, "--dividend_type {none,front,back}"]),
            ("scripts/formula_format_data.py", ["--period", PERIOD_CHOICES_TEXT, "--dividend_type {none,front,back}"]),
            (
                "scripts/diagnostics/run_basic_tq_smoke.py",
                [
                    "--stock_code STOCK_CODE",
                    "--include-write-ops",
                    "--write_block_code WRITE_BLOCK_CODE",
                    "--fail_fast",
                ],
            ),
        ]

        for script_path, snippets in cases:
            with self.subTest(script_path=script_path):
                stdout = self._run_help(script_path)
                for snippet in snippets:
                    self.assertIn(snippet, stdout)

    def test_help_for_int_dividend_type_scripts(self) -> None:
        cases = [
            "scripts/formula_set_data.py",
            "scripts/formula_set_data_info.py",
            "scripts/formula_process_mul_zb.py",
            "scripts/formula_process_mul_xg.py",
            "scripts/formula_process_mul_exp.py",
        ]

        for script_path in cases:
            with self.subTest(script_path=script_path):
                stdout = self._run_help(script_path)
                self.assertIn(PERIOD_CHOICES_TEXT, stdout)
                self.assertIn("--dividend_type {0,1,2}", stdout)


if __name__ == "__main__":
    unittest.main()
