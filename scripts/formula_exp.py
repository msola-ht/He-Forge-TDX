import argparse
import inspect

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import add_formula_preload_arguments, run_formula_preload

parser = argparse.ArgumentParser(description="调用通达信表达式公式")
parser.add_argument("--formula_name", required=True, help="公式名称，区分大小写")
parser.add_argument("--formula_arg", default="", help='公式参数，如: "12,26,9"')
parser.add_argument("--xsflag", type=int, default=-1, help="精度控制，-1 表示默认精度")
add_formula_preload_arguments(parser)
add_output_argument(parser)

args = parser.parse_args()


def _call(tq):
    run_formula_preload(tq, args)
    kwargs = {
        "formula_name": args.formula_name,
        "formula_arg": args.formula_arg,
    }

    signature = inspect.signature(tq.formula_exp)
    if "xsflag" in signature.parameters:
        kwargs["xsflag"] = args.xsflag
    elif args.xsflag != -1:
        raise ValueError("当前 tqcenter.py 的 formula_exp 不支持 xsflag 参数")

    return tq.formula_exp(**kwargs)


data = run_tq_call(__file__, _call)
print_output(data, args.output)
