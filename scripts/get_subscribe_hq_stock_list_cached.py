import argparse

from _bootstrap import add_output_argument, load_subscribe_state, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取已订阅股票列表（带本地缓存回退）")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.get_subscribe_hq_stock_list(),
)

if not data:
    data = load_subscribe_state()

print_output(data, args.output)
