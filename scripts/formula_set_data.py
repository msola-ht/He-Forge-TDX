import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import (
    DIVIDEND_TYPE_INT_CHOICES,
    DIVIDEND_TYPE_INT_HELP_TEXT,
    PERIOD_CHOICES,
    extract_formula_stock_data,
    load_json_file,
)

parser = argparse.ArgumentParser(description="向公式设置K线数据")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument(
    "--stock_period",
    default="1d",
    choices=PERIOD_CHOICES,
    help="K线周期，默认 1d",
)
parser.add_argument(
    "--stock_data_file",
    required=True,
    help="formula_format_data 输出的 JSON 文件路径",
)
parser.add_argument("--count", type=int, default=1, help="生效K线条数，1 到 24000")
parser.add_argument(
    "--dividend_type",
    type=int,
    default=0,
    choices=DIVIDEND_TYPE_INT_CHOICES,
    help=DIVIDEND_TYPE_INT_HELP_TEXT,
)
add_output_argument(parser)

args = parser.parse_args()

raw_data = load_json_file(args.stock_data_file)
stock_data = extract_formula_stock_data(raw_data, args.stock_code)

data = run_tq_call(
    __file__,
    lambda tq: tq.formula_set_data(
        stock_code=args.stock_code,
        stock_period=args.stock_period,
        stock_data=stock_data,
        count=args.count,
        dividend_type=args.dividend_type,
    ),
)
print_output(data, args.output)
