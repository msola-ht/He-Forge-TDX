import argparse

from _bootstrap import add_output_argument, parse_bool, print_output, run_tq_call
from _formula_helpers import (
    DIVIDEND_TYPE_CHOICES,
    DIVIDEND_TYPE_HELP_TEXT,
    FORMULA_REQUIRED_FIELDS,
    PERIOD_CHOICES,
    load_json_file,
)

parser = argparse.ArgumentParser(description="格式化公式所需K线数据")
parser.add_argument(
    "--data_file",
    default="",
    help="可选；get_market_data 的 JSON 输出文件路径。不传时按下方参数实时拉取行情",
)
parser.add_argument(
    "--stock_list",
    nargs="*",
    default=[],
    help="证券代码列表；不传 data_file 时必填，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--period",
    default="1d",
    choices=PERIOD_CHOICES,
    help="K线周期",
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20260101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20260622")
parser.add_argument("--count", type=int, default=-1, help="返回数据个数")
parser.add_argument(
    "--dividend_type",
    default="none",
    choices=DIVIDEND_TYPE_CHOICES,
    help=DIVIDEND_TYPE_HELP_TEXT,
)
parser.add_argument(
    "--fill_data",
    type=parse_bool,
    default=True,
    help="是否填充缺失数据: true/false",
)
add_output_argument(parser)

args = parser.parse_args()

if not args.data_file and not args.stock_list:
    parser.error("不传 --data_file 时，必须提供 --stock_list")


def _call(tq):
    if args.data_file:
        source_data = load_json_file(args.data_file)
    else:
        source_data = tq.get_market_data(
            field_list=FORMULA_REQUIRED_FIELDS,
            stock_list=args.stock_list,
            period=args.period,
            start_time=args.start_time,
            end_time=args.end_time,
            count=args.count,
            dividend_type=args.dividend_type,
            fill_data=args.fill_data,
        )

    return tq.formula_format_data(data_dict=source_data)


data = run_tq_call(__file__, _call)
print_output(data, args.output)
