import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="按日期获取板块交易数据")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="板块代码列表，如: 880660.SH 880515.SH",
)
parser.add_argument(
    "--field_list",
    nargs="*",
    default=[],
    help="板块交易字段列表，如: BK5 BK6 BK9，留空时返回全部字段",
)
parser.add_argument("--year", type=int, default=0, help="年份，如: 2025；0 返回最新")
parser.add_argument(
    "--mmdd",
    type=int,
    default=0,
    help="报告期月日，如: 331、630、930、1231；0 返回最新",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_bkjy_value_by_date(
        stock_list=args.stock_list,
        field_list=args.field_list,
        year=args.year,
        mmdd=args.mmdd,
    ),
)
print_output(data, args.output)
