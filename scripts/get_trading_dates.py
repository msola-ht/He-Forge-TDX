import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取交易日列表")
parser.add_argument("--market", required=True, help="市场代码，如: SH、SZ、HK")
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20261231")
parser.add_argument("--count", type=int, default=-1, help="返回数量限制，-1 表示全部")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_trading_dates(
        market=args.market,
        start_time=args.start_time,
        end_time=args.end_time,
        count=args.count,
    ),
)
print_output(data, args.output)
