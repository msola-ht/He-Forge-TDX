from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from lib.cli import runtime
from lib.cli import basic_tq_smoke


class _FakeTq:
    def __init__(self, stock_list_result):
        self.stock_list_result = stock_list_result
        self.initialized_with = []
        self.closed = 0
        self.stock_list_calls = []

    def initialize(self, entry_file: str) -> None:
        self.initialized_with.append(entry_file)

    def close(self) -> None:
        self.closed += 1

    def get_stock_list(self, *, market, list_type):
        self.stock_list_calls.append((market, list_type))
        return self.stock_list_result


class _FakeSendUserBlockByStockList:
    def __init__(self) -> None:
        self.calls = []

    def send_user_block(self, *, block_code, stock_list, show):
        self.calls.append((block_code, list(stock_list), show))
        return {"ErrorId": "0"}


class _FakeSendUserBlockByStocks:
    def __init__(self) -> None:
        self.calls = []

    def send_user_block(self, *, block_code, stocks, show):
        self.calls.append((block_code, list(stocks), show))
        return {"ErrorId": "0"}


class CliRuntimeTests(unittest.TestCase):
    def test_basic_tq_smoke_detects_empty_json_as_not_meaningful(self) -> None:
        self.assertFalse(basic_tq_smoke._has_meaningful_json(""))
        self.assertFalse(basic_tq_smoke._has_meaningful_json("{}"))
        self.assertFalse(basic_tq_smoke._has_meaningful_json("[]"))
        self.assertTrue(basic_tq_smoke._has_meaningful_json('{"Code":"000001.SZ"}'))
        self.assertTrue(basic_tq_smoke._has_meaningful_json("[1]"))

    def test_run_tq_call_executes_default_connectivity_probe(self) -> None:
        fake_tq = _FakeTq([{"Code": "000001.SZ", "Name": "平安银行"}])

        with patch.object(runtime, "tq", fake_tq):
            result = runtime.run_tq_call(
                "demo.py",
                lambda tq: {"ok": tq is fake_tq},
            )

        self.assertEqual(result, {"ok": True})
        self.assertEqual(fake_tq.initialized_with, ["demo.py"])
        self.assertEqual(fake_tq.stock_list_calls, [("5", 1)])
        self.assertEqual(fake_tq.closed, 1)

    def test_run_tq_call_raises_when_connectivity_probe_returns_empty(self) -> None:
        fake_tq = _FakeTq([])

        with patch.object(runtime, "tq", fake_tq):
            with self.assertRaises(RuntimeError) as ctx:
                runtime.run_tq_call(
                    "demo.py",
                    lambda tq: {"ok": True},
                )

        error_message = str(ctx.exception)
        self.assertIn("TQ 连通性检测失败", error_message)
        self.assertIn("python scripts/diagnose_tdx_path.py --probe stock_list --market 5 --output json", error_message)
        self.assertIn("python scripts/setup_tdx_path.py --show-all --output json", error_message)
        self.assertEqual(fake_tq.closed, 1)

    def test_run_tq_call_can_disable_preflight(self) -> None:
        fake_tq = _FakeTq([])

        with patch.object(runtime, "tq", fake_tq):
            result = runtime.run_tq_call(
                "demo.py",
                lambda tq: {"ok": tq is fake_tq},
                preflight=False,
            )

        self.assertEqual(result, {"ok": True})
        self.assertEqual(fake_tq.stock_list_calls, [])
        self.assertEqual(fake_tq.closed, 1)

    def test_subscribe_state_file_can_be_overridden_by_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = f"{tmpdir}/subscribe-state.json"

            with patch.dict("os.environ", {"TDX_SUBSCRIBE_STATE_FILE": state_file}, clear=False):
                runtime.save_subscribe_state(["600000.SH", "000001.SZ", "600000.SH"])
                loaded = runtime.load_subscribe_state()

        self.assertEqual(loaded, ["000001.SZ", "600000.SH"])

    def test_send_user_block_compat_prefers_stock_list_signature(self) -> None:
        fake_tq = _FakeSendUserBlockByStockList()

        result = runtime.send_user_block_compat(
            fake_tq,
            block_code="LZXG",
            stocks=["000001.SZ"],
            show=True,
        )

        self.assertEqual(result, {"ErrorId": "0"})
        self.assertEqual(fake_tq.calls, [("LZXG", ["000001.SZ"], True)])

    def test_send_user_block_compat_falls_back_to_stocks_signature(self) -> None:
        fake_tq = _FakeSendUserBlockByStocks()

        result = runtime.send_user_block_compat(
            fake_tq,
            block_code="LZXG",
            stocks=["000001.SZ"],
            show=False,
        )

        self.assertEqual(result, {"ErrorId": "0"})
        self.assertEqual(fake_tq.calls, [("LZXG", ["000001.SZ"], False)])

    def test_format_table_renders_mixed_nested_dict_as_sections(self) -> None:
        value = {
            "summary": {
                "selected_count": 0,
                "formula": "C < REF(LLV(L,10),1)",
            },
            "selected": pd.DataFrame(columns=["Code", "Name", "Close", "PrevLow"]),
            "actions": {
                "send_user_block": {
                    "ok": True,
                    "message": "",
                }
            },
        }

        rendered = runtime._format_table(value)

        self.assertIn("[summary]", rendered)
        self.assertIn("| field", rendered)
        self.assertIn("[selected]", rendered)
        self.assertIn("| Code", rendered)
        self.assertIn("[actions]", rendered)
        self.assertIn("| send_user_block", rendered)
        self.assertIn("| ok", rendered)
        self.assertNotIn('{\n  "summary"', rendered)

    def test_markdown_table_uses_compact_terminal_friendly_layout(self) -> None:
        frame = pd.DataFrame(
            [
                {"field": "source_block_code", "value": "通达信88"},
                {"field": "selected_count", "value": 5},
            ]
        )

        rendered = runtime._markdown_table(frame)

        self.assertIn("| field", rendered)
        self.assertIn("| source_block_code", rendered)
        self.assertIn("| ---", rendered)
        self.assertIn("| source_block_code | 通达信88 |", rendered)

    def test_markdown_table_truncates_long_cells_to_fit_terminal_width(self) -> None:
        frame = pd.DataFrame(
            [
                {"field": "formula", "value": "C < REF(LLV(L,10),1) and some very long suffix for terminal clipping"},
            ]
        )

        with patch.object(runtime, "_resolve_table_max_width", return_value=36):
            rendered = runtime._markdown_table(frame)

        self.assertIn("...", rendered)
        self.assertTrue(all(runtime._display_width(line) <= 36 for line in rendered.splitlines()))

    def test_markdown_table_splits_wide_frames_into_multiple_sections(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "BlockCode": "881318.SH",
                    "BlockName": "电子",
                    "StockCount": 533,
                    "SuccessCount": 533,
                    "Zjl": 1414330.01,
                    "Zjl_HB": 763149.02,
                    "AvgZjlPerStock": 2653.53,
                    "AvgZjlHbPerStock": 1431.80,
                    "CurrentRank": 1,
                    "RankChange": 0,
                }
            ]
        )

        with patch.object(runtime, "_resolve_table_max_width", return_value=80):
            rendered = runtime._markdown_table(frame)

        self.assertGreaterEqual(rendered.count("| BlockCode"), 2)
        self.assertIn("AvgZjlPerStock", rendered)
        self.assertIn("CurrentRank", rendered)


if __name__ == "__main__":
    unittest.main()
