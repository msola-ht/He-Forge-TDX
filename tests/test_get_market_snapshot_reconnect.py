from __future__ import annotations

import io
import json
import runpy
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "diagnostics" / "get_market_snapshot_reconnect.py"


class _FakeTq:
    def __init__(self, responses):
        self._responses = list(responses)

    def get_market_snapshot(self, *, stock_code: str, field_list: list[str]):
        if not self._responses:
            raise AssertionError("unexpected get_market_snapshot call")
        return self._responses.pop(0)


class GetMarketSnapshotReconnectTests(unittest.TestCase):
    def _run_script(self, argv: list[str], sessions):
        stdout = io.StringIO()
        session_iter = iter(sessions)

        @contextmanager
        def _fake_tq_session(_entry_file):
            yield next(session_iter)

        with patch("scripts._bootstrap.tq_session", side_effect=_fake_tq_session):
            with patch("time.sleep", return_value=None):
                with patch.object(sys, "argv", ["get_market_snapshot_reconnect.py", *argv]):
                    with patch("sys.stdout", stdout):
                        runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

        return json.loads(stdout.getvalue())

    def test_reconnect_when_snapshot_unchanged(self) -> None:
        result = self._run_script(
            [
                "--stock_code", "AAPL.US",
                "--field_list", "Now", "Volume",
                "--output", "json",
            ],
            sessions=[
                _FakeTq([
                    {"Now": "201.01", "Volume": "100"},
                    {"Now": "201.01", "Volume": "100"},
                ]),
                _FakeTq([
                    {"Now": "201.15", "Volume": "120"},
                ]),
            ],
        )

        self.assertTrue(result["unchanged_in_same_session"])
        self.assertTrue(result["reconnect_attempted"])
        self.assertTrue(result["changed_after_reconnect"])
        self.assertEqual(result["third_fetch"]["data"]["Now"], "201.15")

    def test_skip_reconnect_when_snapshot_changes(self) -> None:
        result = self._run_script(
            [
                "--stock_code", "AAPL.US",
                "--field_list", "Now", "Volume",
                "--output", "json",
            ],
            sessions=[
                _FakeTq([
                    {"Now": "201.01", "Volume": "100"},
                    {"Now": "201.02", "Volume": "110"},
                ]),
            ],
        )

        self.assertFalse(result["unchanged_in_same_session"])
        self.assertFalse(result["reconnect_attempted"])
        self.assertIsNone(result["third_fetch"])

    def test_raise_when_snapshot_is_empty(self) -> None:
        stdout = io.StringIO()

        @contextmanager
        def _fake_tq_session(_entry_file):
            yield _FakeTq([{}])

        with patch("scripts._bootstrap.tq_session", side_effect=_fake_tq_session):
            with patch.object(
                sys,
                "argv",
                [
                    "get_market_snapshot_reconnect.py",
                    "--stock_code", "AAPL.US",
                    "--field_list", "Now",
                    "--output", "json",
                ],
            ):
                with patch("sys.stdout", stdout):
                    with self.assertRaisesRegex(RuntimeError, "get_market_snapshot 返回空结果"):
                        runpy.run_path(str(SCRIPT_PATH), run_name="__main__")


if __name__ == "__main__":
    unittest.main()
