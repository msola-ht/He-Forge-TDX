import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取板块内股票列表")
parser.add_argument(
    "--block_code",
    required=True,
    help="板块代码或板块名称，如: 880515.SH 或 通达信88",
)
parser.add_argument(
    "--block_type",
    type=int,
    default=0,
    choices=[0, 1, 2],
    help="板块类型: 0=板块指数代码/名称, 1=自定义板块, 2=期货板块",
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
    lambda tq: tq.get_stock_list_in_sector(
        block_code=args.block_code,
        block_type=args.block_type,
        list_type=args.list_type,
    ),
)
print_output(data, args.output)
