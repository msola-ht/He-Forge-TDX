import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取专业财务数据")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--field_list",
    nargs="*",
    default=[],
    help="财务字段列表，如: FN1 FN8 FN134，留空时返回全部字段",
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20240101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20261231")
parser.add_argument(
    "--report_type",
    default="report_time",
    choices=["report_time", "announce_time", "tag_time"],
    help="时间维度: report_time=报告期, announce_time=公告时间, tag_time=标签时间",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_financial_data(
        stock_list=args.stock_list,
        field_list=args.field_list,
        start_time=args.start_time,
        end_time=args.end_time,
        report_type=args.report_type,
    ),
)
print_output(data, args.output)
