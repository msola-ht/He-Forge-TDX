import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import add_formula_preload_arguments, run_formula_preload

parser = argparse.ArgumentParser(description="获取当前公式数据")
parser.add_argument(
    "--formula_kind",
    default="",
    choices=["", "zb", "xg", "exp"],
    help="可选；若传入则先执行对应公式，再调用 formula_get_data",
)
parser.add_argument("--formula_name", default="", help="可选；公式名称，区分大小写")
parser.add_argument("--formula_arg", default="", help='公式参数，如: "12,26,9" 或 "3"')
parser.add_argument("--xsflag", type=int, default=-1, help="指标公式精度控制，-1 表示默认精度")
add_formula_preload_arguments(parser)
add_output_argument(parser)

args = parser.parse_args()


def _call(tq):
    run_formula_preload(tq, args)

    if args.formula_kind and not args.formula_name:
        raise ValueError("传入 --formula_kind 时，必须同时提供 --formula_name")

    if args.formula_name:
        if args.formula_kind == "zb":
            tq.formula_zb(
                formula_name=args.formula_name,
                formula_arg=args.formula_arg,
                xsflag=args.xsflag,
            )
        elif args.formula_kind == "xg":
            tq.formula_xg(
                formula_name=args.formula_name,
                formula_arg=args.formula_arg,
            )
        elif args.formula_kind == "exp":
            tq.formula_exp(
                formula_name=args.formula_name,
                formula_arg=args.formula_arg,
            )
        else:
            raise ValueError("传入 --formula_name 时，必须用 --formula_kind 指定 zb/xg/exp")

    return tq.formula_get_data()


data = run_tq_call(__file__, _call)
print_output(data, args.output)
