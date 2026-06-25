import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取市场交易数据")
parser.add_argument("--field_list", nargs="*", default=[], help="字段列表，如: SCJY1 SCJY2")
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20250622")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_scjy_value(
        field_list=args.field_list,
        start_time=args.start_time,
        end_time=args.end_time,
    ),
)
print_output(data, args.output)
