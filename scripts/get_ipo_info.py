import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取新股申购信息")
parser.add_argument(
    "--ipo_type",
    type=int,
    default=0,
    choices=[0, 1, 2],
    help="返回类型: 0=新股申购, 1=新发债, 2=两者都返回",
)
parser.add_argument(
    "--ipo_date",
    type=int,
    default=0,
    choices=[0, 1],
    help="日期范围: 0=只返回今天, 1=今天及以后",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_ipo_info(
        ipo_type=args.ipo_type,
        ipo_date=args.ipo_date,
    ),
)
print_output(data, args.output)
