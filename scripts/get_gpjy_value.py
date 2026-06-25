import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取股票交易数据")
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
    help="交易字段列表，如: GP3 GP14 GP21，留空时返回全部字段",
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20261231")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_gpjy_value(
        stock_list=args.stock_list,
        field_list=args.field_list,
        start_time=args.start_time,
        end_time=args.end_time,
    ),
)
print_output(data, args.output)
