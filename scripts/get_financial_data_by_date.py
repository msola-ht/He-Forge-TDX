import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="按年度/季度获取财务数据")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--field_list",
    nargs="*",
    default=[],
    help="财务字段列表，如: FN1 FN8 FN134，留空时返回全部字段",
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
    lambda tq: tq.get_financial_data_by_date(
        stock_list=args.stock_list,
        field_list=args.field_list,
        year=args.year,
        mmdd=args.mmdd,
    ),
)
print_output(data, args.output)
