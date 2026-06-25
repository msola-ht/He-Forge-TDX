import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="刷新历史K线缓存")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--period",
    required=True,
    choices=["1m", "5m", "1d"],
    help="周期: 1m=一分钟线, 5m=五分钟线, 1d=日线",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.refresh_kline(
        stock_list=args.stock_list,
        period=args.period,
    ),
)
print_output(data, args.output)
