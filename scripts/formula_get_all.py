import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import call_tdx_formula_main

parser = argparse.ArgumentParser(description="获取通达信公式列表")
parser.add_argument(
    "--formula_type",
    type=int,
    default=0,
    choices=[0, 1, 2],
    help="公式类型: 0=技术指标, 1=条件选股, 2=专家系统",
)
add_output_argument(parser)

args = parser.parse_args()


def _call(tq):
    if hasattr(tq, "formula_get_all"):
        result = tq.formula_get_all(formula_type=args.formula_type)
        if result not in ({}, None, []):
            return result

        fallback = call_tdx_formula_main(
            tq,
            {
                "type": 5,
                "formula_type": args.formula_type,
            },
        )
        if fallback.get("ErrorId") in {"0", 0}:
            return fallback.get("Value", fallback)

        return {
            "ErrorId": "EMPTY",
            "Msg": "formula_get_all 已调用，但客户端返回空结果(server return none)",
            "formula_type": args.formula_type,
        }

    result = call_tdx_formula_main(
        tq,
        {
            "type": 5,
            "formula_type": args.formula_type,
        },
    )
    if result.get("ErrorId") in {"0", 0}:
        return result.get("Value", result)

    result["Msg"] = (
        "当前本机 tqcenter.py 未封装 formula_get_all，已尝试底层 TdxFuncMain(type=5) 回退"
        f"，结果: {result.get('Msg') or result.get('Error') or result.get('ErrorId')}"
    )
    return result


data = run_tq_call(
    __file__,
    _call,
)
print_output(data, args.output)
