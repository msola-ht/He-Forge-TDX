from __future__ import annotations

from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "diagnose_tdx_path.py"
SCRIPTS_DIR = str(ROOT / "scripts")


class _FakeProbeTq:
    def get_stock_list(self, **kwargs):
        return []

    def get_market_snapshot(self, **kwargs):
        return {}

    def get_market_data(self, **kwargs):
        return []

    def formula_get_all(self, **kwargs):
        return []

    def formula_get_info(self, **kwargs):
        return {}


class DiagnoseTdxPathTests(unittest.TestCase):
    def _run_script(self, argv: list[str], probe_result):
        calls = []

        if SCRIPTS_DIR not in sys.path:
            sys.path.insert(0, SCRIPTS_DIR)

        import _bootstrap

        def fake_run_tq_call(entry_file: str, callback, **kwargs):
            calls.append(
                {
                    "entry_file": entry_file,
                    "preflight": kwargs.get("preflight"),
                }
            )
            return probe_result

        fake_module = types.SimpleNamespace(tq=_FakeProbeTq())

        with patch.object(_bootstrap, "run_tq_call", side_effect=fake_run_tq_call):
            with patch.object(_bootstrap, "print_output", return_value=None):
                with patch("lib.config.describe_tdx_user_dir_candidates", return_value=[]):
                    with patch("lib.config.find_tdx_user_dir", return_value=None):
                        with patch("lib.config.load_config", return_value={}):
                            with patch("lib.tqcenter._load_external_module", return_value=fake_module):
                                with patch.object(sys, "argv", ["diagnose_tdx_path.py", *argv]):
                                    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

        return calls

    def test_stock_list_probe_bypasses_global_preflight(self) -> None:
        calls = self._run_script(
            ["--probe", "stock_list", "--output", "json"],
            [{"Code": "000001.SZ"}],
        )

        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0]["preflight"])

    def test_market_snapshot_probe_bypasses_global_preflight(self) -> None:
        calls = self._run_script(
            ["--probe", "market_snapshot", "--output", "json"],
            {"Now": 12.34, "LastClose": 12.00, "Open": 12.10},
        )

        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0]["preflight"])


if __name__ == "__main__":
    unittest.main()
