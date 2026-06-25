import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="发送预警信号到客户端")
parser.add_argument("--stock_list", nargs="+", required=True, help="股票代码列表")
parser.add_argument("--price_list", nargs="+", required=True, help="价格列表，纯数字字符串")
parser.add_argument("--close_list", nargs="+", required=True, help="收盘/昨收价列表，纯数字字符串")
parser.add_argument("--volum_list", nargs="+", required=True, help="成交量列表，纯数字字符串")
parser.add_argument("--time_list", nargs="*", default=[], help="时间列表，格式: YYYYMMDDHHMMSS")
parser.add_argument(
    "--bs_flag_list",
    nargs="*",
    default=[],
    help="买卖标志列表: 0=买, 1=卖, 2=未知",
)
parser.add_argument(
    "--warn_type_list",
    nargs="*",
    default=[],
    help="预警类型列表: 1 支持双击闪电买卖，留空时补 -1",
)
parser.add_argument("--reason_list", nargs="*", default=[], help="预警原因列表")
parser.add_argument("--count", type=int, default=1, help="信号数量，必须大于 0")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.send_warn(
        stock_list=args.stock_list,
        time_list=args.time_list,
        price_list=args.price_list,
        close_list=args.close_list,
        volum_list=args.volum_list,
        bs_flag_list=args.bs_flag_list,
        warn_type_list=args.warn_type_list,
        reason_list=args.reason_list,
        count=args.count,
    ),
)
print_output(data, args.output)
