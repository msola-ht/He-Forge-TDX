import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import DIVIDEND_TYPE_INT_CHOICES, DIVIDEND_TYPE_INT_HELP_TEXT, PERIOD_CHOICES

parser = argparse.ArgumentParser(description="向公式设置信息方式的K线数据")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument(
    "--stock_period",
    default="1d",
    choices=PERIOD_CHOICES,
    help="K线周期，默认 1d",
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20260101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20260622")
parser.add_argument(
    "--count",
    type=int,
    default=0,
    help="K线数量: >0按条数, =0按时间区间, =-1全部, =-2无序列数据",
)
parser.add_argument(
    "--dividend_type",
    type=int,
    default=0,
    choices=DIVIDEND_TYPE_INT_CHOICES,
    help=DIVIDEND_TYPE_INT_HELP_TEXT,
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.formula_set_data_info(
        stock_code=args.stock_code,
        stock_period=args.stock_period,
        start_time=args.start_time,
        end_time=args.end_time,
        count=args.count,
        dividend_type=args.dividend_type,
    ),
)
print_output(data, args.output)
