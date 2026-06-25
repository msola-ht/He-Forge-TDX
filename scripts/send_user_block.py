import argparse

from _bootstrap import add_output_argument, parse_bool, print_output, run_tq_call, send_user_block_compat

parser = argparse.ArgumentParser(description="发送股票到自定义板块")
parser.add_argument(
    "--block_code",
    default="",
    help='目标板块简称；为空字符串时发送到"临时条件股"板块，非空时该板块必须已存在',
)
parser.add_argument(
    "--stocks",
    nargs="*",
    default=[],
    help="股票代码列表；传空列表时表示清空板块",
)
parser.add_argument(
    "--show",
    type=parse_bool,
    default=False,
    help="是否在客户端自动跳转显示该板块: true/false",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: send_user_block_compat(
        tq,
        block_code=args.block_code,
        stocks=args.stocks,
        show=args.show,
    ),
)
print_output(data, args.output)
