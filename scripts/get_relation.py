import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取股票所属板块信息")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_relation(stock_code=args.stock_code),
)
print_output(data, args.output)
