import json

from lib.tq_constants import (
    DIVIDEND_TYPE_CHOICES,
    DIVIDEND_TYPE_HELP_TEXT,
    DIVIDEND_TYPE_INT_CHOICES,
    DIVIDEND_TYPE_INT_HELP_TEXT,
    PERIOD_CHOICES,
)
from lib.tqcenter import _load_external_module

FORMULA_REQUIRED_FIELDS = ["Amount", "Volume", "Close", "Open", "High", "Low"]


def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_formula_stock_data(raw_data, stock_code: str):
    if isinstance(raw_data, list):
        return raw_data

    if isinstance(raw_data, dict):
        if stock_code in raw_data and isinstance(raw_data[stock_code], list):
            return raw_data[stock_code]

        if len(raw_data) == 1:
            only_value = next(iter(raw_data.values()))
            if isinstance(only_value, list):
                return only_value

    raise ValueError(
        "无法从输入文件中解析公式数据，请传入 formula_format_data 的输出，"
        "或确保文件中包含目标 stock_code 对应的列表数据"
    )


def add_formula_prepare_arguments(parser) -> None:
    parser.add_argument(
        "--stock_code",
        default="",
        help="可选；传入后会先调用 formula_set_data_info 预载该证券数据",
    )
    parser.add_argument(
        "--stock_period",
        default="1d",
        choices=PERIOD_CHOICES,
        help="预载数据周期，默认 1d",
    )
    parser.add_argument("--start_time", default="", help="预载起始时间，格式如: 20260101")
    parser.add_argument("--end_time", default="", help="预载结束时间，格式如: 20260622")
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="预载K线数量: >0按条数, =0按时间区间, =-1全部, =-2无序列数据",
    )
    parser.add_argument(
        "--dividend_type",
        type=int,
        default=0,
        choices=DIVIDEND_TYPE_INT_CHOICES,
        help=f"预载{DIVIDEND_TYPE_INT_HELP_TEXT}",
    )


def maybe_formula_set_data_info(tq, args):
    if not args.stock_code:
        return None

    return tq.formula_set_data_info(
        stock_code=args.stock_code,
        stock_period=args.stock_period,
        start_time=args.start_time,
        end_time=args.end_time,
        count=args.count,
        dividend_type=args.dividend_type,
    )


def add_formula_preload_arguments(parser) -> None:
    parser.add_argument(
        "--prepare_stock_code",
        default="",
        help="可选；传入后会在公式执行前预载该证券数据",
    )
    parser.add_argument(
        "--prepare_stock_period",
        default="1d",
        choices=PERIOD_CHOICES,
        help="预载数据周期，默认 1d",
    )
    parser.add_argument("--prepare_start_time", default="", help="预载起始时间，格式如: 20260101")
    parser.add_argument("--prepare_end_time", default="", help="预载结束时间，格式如: 20260622")
    parser.add_argument(
        "--prepare_count",
        type=int,
        default=0,
        help="预载K线数量；用于 data_info 时 >0按条数, =0按时间区间, =-1全部, =-2无序列",
    )
    parser.add_argument(
        "--prepare_dividend_type",
        type=int,
        default=0,
        choices=DIVIDEND_TYPE_INT_CHOICES,
        help=f"预载{DIVIDEND_TYPE_INT_HELP_TEXT}",
    )
    parser.add_argument(
        "--prepare_stock_data_file",
        default="",
        help="可选；formula_format_data 输出文件，传入后先调用 formula_set_data",
    )


def run_formula_preload(tq, args):
    if args.prepare_stock_data_file:
        if not args.prepare_stock_code:
            raise ValueError("使用 --prepare_stock_data_file 时，必须同时提供 --prepare_stock_code")

        raw_data = load_json_file(args.prepare_stock_data_file)
        stock_data = extract_formula_stock_data(raw_data, args.prepare_stock_code)
        effective_count = args.prepare_count if args.prepare_count > 0 else len(stock_data)

        return tq.formula_set_data(
            stock_code=args.prepare_stock_code,
            stock_period=args.prepare_stock_period,
            stock_data=stock_data,
            count=effective_count,
            dividend_type=args.prepare_dividend_type,
        )

    if args.prepare_stock_code:
        return tq.formula_set_data_info(
            stock_code=args.prepare_stock_code,
            stock_period=args.prepare_stock_period,
            start_time=args.prepare_start_time,
            end_time=args.prepare_end_time,
            count=args.prepare_count,
            dividend_type=args.prepare_dividend_type,
        )

    return None


def call_tdx_formula_main(tq, payload: dict, timeout_ms: int = 60000):
    module = _load_external_module()
    payload = dict(payload)
    payload["id"] = tq._get_run_id()
    json_str = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ptr = module.dll.TdxFuncMain(tq._get_run_id(), json_str, timeout_ms)
    if not ptr or len(ptr) == 0:
        return {
            "ErrorId": "EMPTY",
            "Msg": "TdxFuncMain 返回空指针",
            "payload": payload,
        }

    result_str = ptr.decode("utf-8")
    try:
        return module._json_loads_with_errorid_guard(result_str)
    except Exception:
        return {
            "ErrorId": "RAW",
            "Msg": result_str,
            "payload": payload,
        }


def ensure_batch_formula_result(raw_result, *, action_name: str):
    if not isinstance(raw_result, dict):
        raise RuntimeError(f"{action_name} 返回结果不是 dict")

    error_id = str(raw_result.get("ErrorId", "0")).strip()
    if error_id not in {"", "0", "None"}:
        raise RuntimeError(
            f"{action_name} 返回错误：ErrorId={error_id}, Msg={raw_result.get('Msg', '')}"
        )

    has_stock_payload = any(isinstance(value, dict) for value in raw_result.values())
    message = str(raw_result.get("Msg", "")).strip()
    if not has_stock_payload and message:
        raise RuntimeError(f"{action_name} 返回错误：{message}")

    return raw_result


def build_copyable_formula_text(
    *,
    formula_name: str,
    formula_body: str | None,
    formula_type: str = "条件选股",
    parameter_lines: list[str] | None = None,
    fallback_body_hint: str | None = None,
) -> str:
    body_text = formula_body
    if body_text is None:
        body_text = fallback_body_hint or f"当前模块未内置 {formula_name} 的公式正文，请使用客户端现有公式或自定义同名公式。"

    lines = [
        "正文直接粘贴：",
        body_text,
        "",
        "界面字段：",
        f"公式名称={formula_name}",
        f"公式类型={formula_type}",
    ]
    for parameter_line in parameter_lines or []:
        lines.append(parameter_line)
    return "\n".join(lines)
