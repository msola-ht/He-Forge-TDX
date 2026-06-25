from __future__ import annotations

import argparse
from datetime import datetime, time as dt_time
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


def _is_in_core_trading_session(now_dt: datetime) -> bool:
    current_time = now_dt.astimezone().time() if now_dt.tzinfo is not None else now_dt.time()
    return (
        dt_time(hour=9, minute=30) <= current_time <= dt_time(hour=11, minute=30)
        or dt_time(hour=13, minute=0) <= current_time <= dt_time(hour=15, minute=0)
    )


def _fetch_more_info(tq, *, stock_code: str, field_list: list[str]):
    return tq.get_more_info(
        stock_code=stock_code,
        field_list=field_list,
    )


parser = argparse.ArgumentParser(description="获取证券扩展信息；若连续两次完全不变，则断开重连后再取一次")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 300750.SZ")
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
    "--reconnect_out_of_session",
    type=parse_bool,
    default=False,
    help="是否允许在非盘中时段也因两次完全不变而断连重取: true/false，默认 false",
)
add_output_argument(parser)

args = parser.parse_args()

if args.interval_seconds < 0:
    raise ValueError("--interval_seconds 不能小于 0")

with tq_session(__file__) as tq:
    first_data = _fetch_more_info(
        tq,
        stock_code=args.stock_code,
        field_list=args.field_list,
    )
    first_fetched_at = _now_iso()

    if args.interval_seconds > 0:
        time.sleep(args.interval_seconds)

    second_data = _fetch_more_info(
        tq,
        stock_code=args.stock_code,
        field_list=args.field_list,
    )
    second_fetched_at = _now_iso()

unchanged_in_same_session = first_data == second_data
now_dt = datetime.now().astimezone()
in_core_trading_session = _is_in_core_trading_session(now_dt)
should_reconnect = unchanged_in_same_session and (
    in_core_trading_session or args.reconnect_out_of_session
)

result = {
    "stock_code": args.stock_code,
    "field_list": args.field_list,
    "interval_seconds": float(args.interval_seconds),
    "in_core_trading_session": in_core_trading_session,
    "reconnect_out_of_session": bool(args.reconnect_out_of_session),
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
    "reconnect_skipped_reason": None,
}

if should_reconnect:
    with tq_session(__file__) as tq:
        third_data = _fetch_more_info(
            tq,
            stock_code=args.stock_code,
            field_list=args.field_list,
        )
        third_fetched_at = _now_iso()

    result["reconnect_attempted"] = True
    result["changed_after_reconnect"] = third_data != second_data
    result["third_fetch"] = {
        "fetched_at": third_fetched_at,
        "data": third_data,
    }
elif unchanged_in_same_session and not in_core_trading_session and not args.reconnect_out_of_session:
    result["reconnect_skipped_reason"] = "non_trading_session"

print_output(result, args.output)
