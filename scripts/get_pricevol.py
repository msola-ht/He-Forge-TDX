import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取股票价格和成交量数据")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_pricevol(stock_list=args.stock_list),
)
print_output(data, args.output)
