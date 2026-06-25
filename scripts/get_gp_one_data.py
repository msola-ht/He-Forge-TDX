import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取股票单个数据字段")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--field_list",
    nargs="+",
    required=True,
    help="字段列表，如: GO1 GO3 GO10",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_gp_one_data(
        stock_list=args.stock_list,
        field_list=args.field_list,
    ),
)
print_output(data, args.output)
