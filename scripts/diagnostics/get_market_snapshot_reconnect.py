from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from scripts._bootstrap import add_output_argument, parse_bool, print_output, tq_session


def _now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _fetch_market_snapshot(tq, *, stock_code: str, field_list: list[str]):
    return tq.get_market_snapshot(
        stock_code=stock_code,
        field_list=field_list,
    )


def _ensure_non_empty_snapshot(data, *, stock_code: str) -> None:
    if data:
        return
    raise RuntimeError(
        "get_market_snapshot 返回空结果，当前 stock_code 可能无效，或该客户端当前不支持该市场代码。"
        f"请先运行 `python scripts/get_match_stkinfo.py --key_word {stock_code} --output json` "
        "确认真实证券代码后再重试。"
    )


parser = argparse.ArgumentParser(description="获取实时快照；若连续两次完全不变，则断开重连后再取一次")
parser.add_argument("--stock_code", required=True, help="证券代码，如: AAPL.US")
parser.add_argument(
    "--field_list",
    nargs="*",
    default=[],
    help="字段筛选列表，留空时返回全部字段",
)
parser.add_argument(
    "--interval_seconds",
    type=float,
    default=1.0,
    help="同一连接内两次获取之间的等待秒数，默认 1",
)
parser.add_argument(
    "--reconnect_on_unchanged",
    type=parse_bool,
    default=True,
    help="两次完全不变时是否断连重取: true/false，默认 true",
)
add_output_argument(parser)

args = parser.parse_args()

if args.interval_seconds < 0:
    raise ValueError("--interval_seconds 不能小于 0")

with tq_session(__file__) as tq:
    first_data = _fetch_market_snapshot(
        tq,
        stock_code=args.stock_code,
        field_list=args.field_list,
    )
    _ensure_non_empty_snapshot(first_data, stock_code=args.stock_code)
    first_fetched_at = _now_iso()

    if args.interval_seconds > 0:
        time.sleep(args.interval_seconds)

    second_data = _fetch_market_snapshot(
        tq,
        stock_code=args.stock_code,
        field_list=args.field_list,
    )
    _ensure_non_empty_snapshot(second_data, stock_code=args.stock_code)
    second_fetched_at = _now_iso()

unchanged_in_same_session = first_data == second_data
should_reconnect = unchanged_in_same_session and args.reconnect_on_unchanged

result = {
    "stock_code": args.stock_code,
    "field_list": args.field_list,
    "interval_seconds": float(args.interval_seconds),
    "reconnect_on_unchanged": bool(args.reconnect_on_unchanged),
    "first_fetch": {
        "fetched_at": first_fetched_at,
        "data": first_data,
    },
    "second_fetch": {
        "fetched_at": second_fetched_at,
        "data": second_data,
    },
    "unchanged_in_same_session": unchanged_in_same_session,
    "reconnect_attempted": False,
    "changed_after_reconnect": None,
    "third_fetch": None,
}

if should_reconnect:
    with tq_session(__file__) as tq:
        third_data = _fetch_market_snapshot(
            tq,
            stock_code=args.stock_code,
            field_list=args.field_list,
        )
        _ensure_non_empty_snapshot(third_data, stock_code=args.stock_code)
        third_fetched_at = _now_iso()

    result["reconnect_attempted"] = True
    result["changed_after_reconnect"] = third_data != second_data
    result["third_fetch"] = {
        "fetched_at": third_fetched_at,
        "data": third_data,
    }

print_output(result, args.output)
