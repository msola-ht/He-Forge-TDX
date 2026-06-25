import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取交易日历")
parser.add_argument("--market", required=True, help="市场代码，如: SH、SZ、HK")
parser.add_argument("--start_time", required=True, help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", required=True, help="结束时间，格式如: 20261231")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_trading_calendar(
        market=args.market,
        start_time=args.start_time,
        end_time=args.end_time,
    ),
)
print_output(data, args.output)
