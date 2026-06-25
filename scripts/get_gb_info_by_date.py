import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="按日期区间获取股本信息")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument("--start_date", required=True, help="起始日期，格式如: 20240101")
parser.add_argument("--end_date", default="", help="结束日期，格式如: 20250622；不传则默认当前时间")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_gb_info_by_date(
        stock_code=args.stock_code,
        start_date=args.start_date,
        end_date=args.end_date,
    ),
)
print_output(data, args.output)
