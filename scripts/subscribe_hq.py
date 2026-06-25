import argparse
import json
import time

from _bootstrap import add_output_argument, parse_bool, print_output, remember_subscriptions, tq_session

parser = argparse.ArgumentParser(description="订阅行情更新")
parser.add_argument(
    "--stock_list",
    nargs="+",
    required=True,
    help="证券代码列表，如: 688318.SH 000001.SZ",
)
parser.add_argument(
    "--keep_alive",
    type=parse_bool,
    default=False,
    help="订阅后是否保持脚本运行以持续接收回调: true/false",
)
parser.add_argument(
    "--keep_alive_seconds",
    type=int,
    default=0,
    help="保持运行秒数；仅当 keep_alive=true 时生效，0 表示一直运行到手动中断",
)
add_output_argument(parser)

args = parser.parse_args()


def _on_data(datas):
    if args.keep_alive:
        print(datas)
    return None

with tq_session(__file__) as tq:
    data = tq.subscribe_hq(stock_list=args.stock_list, callback=_on_data)

    if isinstance(data, str):
        try:
            result = json.loads(data)
        except json.JSONDecodeError:
            result = {}
        if result.get("ErrorId") == "0":
            remember_subscriptions(args.stock_list)

    print_output(data, args.output)

    if args.keep_alive:
        deadline = None if args.keep_alive_seconds <= 0 else time.time() + args.keep_alive_seconds
        try:
            while deadline is None or time.time() < deadline:
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
