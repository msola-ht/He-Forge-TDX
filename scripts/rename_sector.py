import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="重命名自定义板块")
parser.add_argument("--block_code", required=True, help="板块简称，不能为空")
parser.add_argument("--block_name", required=True, help="新的板块显示名称，不能为空")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.rename_sector(
        block_code=args.block_code,
        block_name=args.block_name,
    ),
)
print_output(data, args.output)
