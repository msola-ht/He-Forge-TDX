import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取股本信息")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument(
    "--date_list",
    nargs="+",
    required=True,
    help="日期列表，格式如: 20250101 20250601，需按从小到大排序",
)
parser.add_argument("--count", type=int, default=1, help="返回日期数量，必须大于等于 1")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_gb_info(
        stock_code=args.stock_code,
        date_list=args.date_list,
        count=args.count,
    ),
)
print_output(data, args.output)
