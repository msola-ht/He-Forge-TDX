import argparse
import time

from _bootstrap import add_output_argument, parse_bool, print_output, tq_session
from lib.tq_constants import (
    DIVIDEND_TYPE_CHOICES,
    DIVIDEND_TYPE_HELP_TEXT,
    PERIOD_CHOICES,
    PERIOD_HELP_TEXT,
    dividend_type_to_int,
)
from lib.tqcenter import _load_external_module

parser = argparse.ArgumentParser(description="订阅单股行情数据回调")
parser.add_argument("--stock_code", required=True, help="证券代码，如: 688318.SH")
parser.add_argument(
    "--period",
    default="1d",
    choices=PERIOD_CHOICES,
    help=PERIOD_HELP_TEXT,
)
parser.add_argument("--start_time", default="", help="起始时间，格式如: 20260101")
parser.add_argument("--end_time", default="", help="结束时间，格式如: 20260622")
parser.add_argument("--count", type=int, default=0, help="返回数据个数")
parser.add_argument(
    "--dividend_type",
    default="none",
    choices=DIVIDEND_TYPE_CHOICES,
    help=DIVIDEND_TYPE_HELP_TEXT,
)
parser.add_argument(
    "--print_callback",
    type=parse_bool,
    default=False,
    help="是否在回调中打印推送内容: true/false",
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


def _on_data(data):
    if args.print_callback:
        try:
            print(data)
        except Exception:
            pass


def _subscribe_quote_direct(tq):
    module = _load_external_module()
    module.dll.SubscribeGPData.restype = module.ctypes.c_char_p

    if not args.stock_code:
        raise ValueError("stock_code 不能为空")

    if not args.period:
        raise ValueError("period 不能为空")

    if not module.check_stock_code_format(args.stock_code):
        raise ValueError(f"{args.stock_code}异常")

    if args.count < 0:
        if not args.start_time:
            raise ValueError("当 count < 0 时必须提供 start_time")
        if not args.end_time:
            raise ValueError("当 count < 0 时必须提供 end_time")

    start_time = module._convert_time_format(args.start_time) if args.start_time else ""
    end_time = module._convert_time_format(args.end_time) if args.end_time else ""

    dividend_type_int = dividend_type_to_int(args.dividend_type)

    if module.is_callback_func(_on_data) is False:
        raise ValueError("回调函数格式错误")

    if tq.m_is_init_data_transfer is False:
        callback_func_type = module.ctypes.CFUNCTYPE(None, module.ctypes.c_char_p)
        tq.data_transfer = callback_func_type(tq._data_callback_transfer)
        module.dll.Register_DataTransferFunc(tq._get_run_id(), tq.data_transfer)
        tq.m_is_init_data_transfer = True

    with tq._callback_lock:
        tq.data_callback_func[tq._get_run_id()][args.stock_code] = _on_data

    codestr = args.stock_code.encode("utf-8")
    startimestr = start_time.encode("utf-8")
    endtimestr = end_time.encode("utf-8")
    periodstr = args.period.encode("utf-8")

    timeout_ms = 5000
    ptr = module.dll.SubscribeGPData(
        tq._get_run_id(),
        codestr,
        startimestr,
        endtimestr,
        periodstr,
        dividend_type_int,
        args.count,
        timeout_ms,
    )
    if ptr is None or len(ptr) == 0:
        return {
            "ErrorId": "EMPTY",
            "Msg": f"订阅{args.stock_code}失败: 返回空指针",
        }

    result_str = ptr.decode("utf-8")
    json_res = module._json_loads_with_errorid_guard(result_str)
    if json_res.get("ErrorId") != "0":
        return {
            "ErrorId": str(json_res.get("ErrorId", "")),
            "Msg": json_res.get("Error") or json_res.get("Msg") or f"订阅{args.stock_code}失败",
        }
    return result_str


with tq_session(__file__) as tq:
    data = _subscribe_quote_direct(tq)
    print_output(data, args.output)

    if args.keep_alive and isinstance(data, str):
        deadline = None if args.keep_alive_seconds <= 0 else time.time() + args.keep_alive_seconds
        try:
            while deadline is None or time.time() < deadline:
                time.sleep(0.2)
        except KeyboardInterrupt:
            pass
