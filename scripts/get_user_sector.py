import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call

parser = argparse.ArgumentParser(description="获取用户自选股板块列表")
add_output_argument(parser)

args = parser.parse_args()

data = run_tq_call(__file__, lambda tq: tq.get_user_sector())
print_output(data, args.output)
