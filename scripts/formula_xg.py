import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import add_formula_preload_arguments, run_formula_preload

parser = argparse.ArgumentParser(description="调用通达信选股公式")
parser.add_argument("--formula_name", required=True, help="公式名称，区分大小写")
parser.add_argument("--formula_arg", default="", help='公式参数，如: "3"')
add_formula_preload_arguments(parser)
add_output_argument(parser)

args = parser.parse_args()


def _call(tq):
    run_formula_preload(tq, args)
    return tq.formula_xg(
        formula_name=args.formula_name,
        formula_arg=args.formula_arg,
    )


data = run_tq_call(__file__, _call)
print_output(data, args.output)
