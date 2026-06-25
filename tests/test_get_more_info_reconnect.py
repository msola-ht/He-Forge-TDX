from __future__ import annotations

from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "diagnostics" / "get_more_info_reconnect.py"
SCRIPTS_DIR = str(ROOT / "scripts")


class _FakeTq:
    def __init__(self, results: list[dict]) -> None:
        self.results = list(results)
        self.calls = []

    def get_more_info(self, *, stock_code: str, field_list: list[str]):
        self.calls.append(
            {
                "stock_code": stock_code,
                "field_list": list(field_list),
            }
        )
        return self.results.pop(0)


class _FakeSession:
    def __init__(self, tq_obj) -> None:
        self.tq_obj = tq_obj

    def __enter__(self):
        return self.tq_obj

    def __exit__(self, exc_type, exc, tb):
        return False


class GetMoreInfoReconnectTests(unittest.TestCase):
    def _run_script(self, argv: list[str], session_tqs: list[_FakeTq]):
        if SCRIPTS_DIR not in sys.path:
            sys.path.insert(0, SCRIPTS_DIR)

        from scripts import _bootstrap

        session_iter = iter(session_tqs)
        outputs = []

        def fake_tq_session(entry_file: str, **kwargs):
            return _FakeSession(next(session_iter))

        def fake_print_output(value, output: str):
            outputs.append((value, output))

        with patch.object(_bootstrap, "tq_session", side_effect=fake_tq_session):
            with patch.object(_bootstrap, "print_output", side_effect=fake_print_output):
                with patch("time.sleep", return_value=None):
                    with patch.object(sys, "argv", ["get_more_info_reconnect.py", *argv]):
                        runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

        return outputs

    def test_reconnects_when_two_fetches_are_unchanged(self) -> None:
        first_session = _FakeTq(
            [
                {"Zjl": "1.0", "Zjl_HB": "2.0"},
                {"Zjl": "1.0", "Zjl_HB": "2.0"},
            ]
        )
        second_session = _FakeTq(
            [
                {"Zjl": "3.0", "Zjl_HB": "4.0"},
            ]
        )

        outputs = self._run_script(
            [
                "--stock_code", "300750.SZ",
                "--field_list", "Zjl", "Zjl_HB",
                "--interval_seconds", "0",
                "--reconnect_out_of_session", "true",
                "--output", "json",
            ],
            [first_session, second_session],
        )

        payload, output_mode = outputs[-1]
        self.assertEqual(output_mode, "json")
        self.assertTrue(payload["unchanged_in_same_session"])
        self.assertTrue(payload["reconnect_attempted"])
        self.assertTrue(payload["changed_after_reconnect"])
        self.assertEqual(payload["third_fetch"]["data"]["Zjl"], "3.0")
        self.assertIsNone(payload["reconnect_skipped_reason"])

    def test_skips_reconnect_when_second_fetch_changes(self) -> None:
        first_session = _FakeTq(
            [
                {"Zjl": "1.0", "Zjl_HB": "2.0"},
                {"Zjl": "5.0", "Zjl_HB": "6.0"},
            ]
        )

        outputs = self._run_script(
            [
                "--stock_code", "300750.SZ",
                "--field_list", "Zjl", "Zjl_HB",
                "--interval_seconds", "0",
                "--output", "json",
            ],
            [first_session],
        )

        payload, output_mode = outputs[-1]
        self.assertEqual(output_mode, "json")
        self.assertFalse(payload["unchanged_in_same_session"])
        self.assertFalse(payload["reconnect_attempted"])
        self.assertIsNone(payload["changed_after_reconnect"])
        self.assertIsNone(payload["third_fetch"])

    def test_skips_reconnect_out_of_session_by_default_when_unchanged(self) -> None:
        first_session = _FakeTq(
            [
                {"Zjl": "1.0", "Zjl_HB": "2.0"},
                {"Zjl": "1.0", "Zjl_HB": "2.0"},
            ]
        )

        outputs = self._run_script(
            [
                "--stock_code", "300750.SZ",
                "--field_list", "Zjl", "Zjl_HB",
                "--interval_seconds", "0",
                "--output", "json",
            ],
            [first_session],
        )

        payload, output_mode = outputs[-1]
        self.assertEqual(output_mode, "json")
        self.assertTrue(payload["unchanged_in_same_session"])
        self.assertFalse(payload["reconnect_attempted"])
        self.assertEqual(payload["reconnect_skipped_reason"], "non_trading_session")


if __name__ == "__main__":
    unittest.main()
