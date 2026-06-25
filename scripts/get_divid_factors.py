import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取分红配送数据")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20261231")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_divid_factors(
        stock_code=args.stock_code,
        start_time=args.start_time,
        end_time=args.end_time,
    ),
)
print_output(data, args.output)
