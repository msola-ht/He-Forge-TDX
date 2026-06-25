import argparse
import json

from _bootstrap import add_output_argument, forget_subscriptions, print_output, run_tq_call

parser = argparse.ArgumentParser(description="取消订阅行情更新")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.unsubscribe_hq(stock_list=args.stock_list),
)

if isinstance(data, str):
    try:
        result = json.loads(data)
    except json.JSONDecodeError:
        result = {}
    if result.get("ErrorId") == "0":
        forget_subscriptions(args.stock_list)

print_output(data, args.output)
