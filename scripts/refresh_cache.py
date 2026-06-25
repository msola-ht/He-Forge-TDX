import argparse

from _bootstrap import add_output_argument, parse_bool, print_output, run_tq_call

parser = argparse.ArgumentParser(description="刷新行情缓存")
parser.add_argument(
    "--market",
    default="AG",
    choices=["AG", "HK", "US", "QH", "QQ", "NQ", "ZZ", "ZS", "OF"],
    help="市场代码，默认 AG",
)
parser.add_argument(
    "--force",
    type=parse_bool,
    default=False,
    help="是否强制刷新: true/false",
)
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(
    __file__,
    lambda tq: tq.refresh_cache(
        market=args.market,
        force=args.force,
    ),
)
print_output(data, args.output)
