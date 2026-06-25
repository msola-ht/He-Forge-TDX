import argparse

from _bootstrap import add_output_argument, parse_bool, print_output, run_tq_call
from _formula_helpers import DIVIDEND_TYPE_INT_CHOICES, DIVIDEND_TYPE_INT_HELP_TEXT, PERIOD_CHOICES

parser = argparse.ArgumentParser(description="批量调用通达信选股公式")
parser.add_argument("--formula_name", required=True, help="公式名称，区分大小写")
parser.add_argument("--formula_arg", default="", help='公式参数，如: "3"')
parser.add_argument("--return_count", type=int, default=1, help="每只股票返回结果数量")
parser.add_argument(
    "--return_date",
    type=parse_bool,
    default=False,
    help="是否返回日期: true/false",
)
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--stock_period",
    default="1d",
    choices=PERIOD_CHOICES,
    help="K线周期，默认 1d",
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20260101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20260622")
parser.add_argument("--count", type=int, default=0, help="行情数据条数")
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
    lambda tq: tq.formula_process_mul_xg(
        formula_name=args.formula_name,
        formula_arg=args.formula_arg,
        return_count=args.return_count,
        return_date=args.return_date,
        stock_list=args.stock_list,
        stock_period=args.stock_period,
        start_time=args.start_time,
        end_time=args.end_time,
        count=args.count,
        dividend_type=args.dividend_type,
    ),
)
print_output(data, args.output)
