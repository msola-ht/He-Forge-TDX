import argparse

from _bootstrap import add_output_argument, print_output, run_tq_call
from _formula_helpers import call_tdx_formula_main

parser = argparse.ArgumentParser(description="获取通达信公式详情")
parser.add_argument(
    "--formula_type",
    type=int,
    default=0,
    choices=[0, 1, 2],
    help="公式类型: 0=技术指标, 1=条件选股, 2=专家系统",
)
parser.add_argument("--formula_code", required=True, help="公式代码，如: MACD")
add_output_argument(parser)

args = parser.parse_args()


def _call(tq):
    if hasattr(tq, "formula_get_info"):
        result = tq.formula_get_info(
            formula_type=args.formula_type,
            formula_code=args.formula_code,
        )
        if result not in ({}, None, []):
            return result

        fallback = call_tdx_formula_main(
            tq,
            {
                "type": 6,
                "formula_type": args.formula_type,
                "formula_code": args.formula_code,
            },
        )
        if fallback.get("ErrorId") in {"0", 0}:
            return fallback.get("Value", fallback)

        return {
            "ErrorId": "EMPTY",
            "Msg": "formula_get_info 已调用，但客户端返回空结果(server return none)",
            "formula_type": args.formula_type,
            "formula_code": args.formula_code,
        }

    result = call_tdx_formula_main(
        tq,
        {
            "type": 6,
            "formula_type": args.formula_type,
            "formula_code": args.formula_code,
        },
    )
    if result.get("ErrorId") in {"0", 0}:
        return result.get("Value", result)

    result["Msg"] = (
        "当前本机 tqcenter.py 未封装 formula_get_info，已尝试底层 TdxFuncMain(type=6) 回退"
        f"，结果: {result.get('Msg') or result.get('Error') or result.get('ErrorId')}"
    )
    result["formula_code"] = args.formula_code
    return result


data = run_tq_call(
    __file__,
    _call,
)
print_output(data, args.output)
