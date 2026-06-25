import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取系统分类股票列表")
parser.add_argument(
    "--market",
    default=None,
    help="市场/分类代码，如 5=所有A股, 31=ETF基金, 92=国内期货主力合约",
)
parser.add_argument(
    "--list_type",
    type=int,
    default=0,
    choices=[0, 1],
    help="返回数据类型: 0=只返回代码, 1=返回代码和名称",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_stock_list(
        market=args.market,
        list_type=args.list_type,
    ),
)
print_output(data, args.output)
