import argparse

from _bootstrap import add_output_argument, parse_bool, print_output, run_tq_call
from lib.tq_constants import DIVIDEND_TYPE_CHOICES, DIVIDEND_TYPE_HELP_TEXT, PERIOD_CHOICES, PERIOD_HELP_TEXT

parser = argparse.ArgumentParser(description="获取K线行情数据")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--period",
    default="1d",
    choices=PERIOD_CHOICES,
    help=PERIOD_HELP_TEXT,
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20251220")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20251220")
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
parser.add_argument("--field_list", nargs="*", default=[], help="字段筛选列表")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_market_data(
        field_list=args.field_list,
        stock_list=args.stock_list,
        period=args.period,
        start_time=args.start_time,
        end_time=args.end_time,
        count=args.count,
        dividend_type=args.dividend_type,
        fill_data=args.fill_data,
    ),
)
print_output(data, args.output)
