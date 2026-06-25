import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取可转债信息")
parser.add_argument(
    "--stock_code",
    required=True,
    help="可转债代码，如: 810014.BJ；测试时建议先用 get_stock_list --market 32 获取当前实际可用代码",
)
parser.add_argument(
    "--field_list",
    nargs="*",
    default=[],
    help="字段筛选列表，留空时返回全部字段",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_kzz_info(
        stock_code=args.stock_code,
        field_list=args.field_list,
    ),
)
print_output(data, args.output)
