import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="按指定日期获取市场交易数据")
parser.add_argument("--field_list", nargs="*", default=[], help="字段列表，如: SCJY1 SCJY2")
parser.add_argument("--year", type=int, default=0, help="年份，如: 2024；0 表示按最新")
parser.add_argument("--mmdd", type=int, default=0, help="月日，如: 1231；0 表示按最新")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_scjy_value_by_date(
        field_list=args.field_list,
        year=args.year,
        mmdd=args.mmdd,
    ),
)
print_output(data, args.output)
