from __future__ import annotations

import importlib
import os
import runpy
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


SCRIPTS_PACKAGE_NAME = "scripts"
PROGRAM_LABEL_ENV_VAR = "TDX_UNIFIED_PROGRAM_LABEL"


@dataclass(frozen=True)
class CommandSpec:
    script_name: str
    category: str
    summary: str

    @property
    def command_name(self) -> str:
        return Path(self.script_name).stem.replace("_", "-")

    @property
    def module_name(self) -> str:
        return f"{SCRIPTS_PACKAGE_NAME}.{Path(self.script_name).stem}"


CATEGORY_SPECS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "路径与诊断",
        [
            ("setup_tdx_path.py", "选择并保存通达信目录"),
            ("diagnose_tdx_path.py", "诊断路径与基础连通性"),
        ],
    ),
    (
        "行情与市场",
        [
            ("get_market_snapshot.py", "获取实时行情快照"),
            ("get_market_data.py", "获取 K 线行情数据"),
            ("get_stock_list.py", "获取系统分类股票列表"),
            ("get_stock_info.py", "获取证券基础信息"),
            ("get_stock_list_in_sector.py", "获取板块成分股"),
            ("get_sector_list.py", "获取系统板块列表"),
            ("get_user_sector.py", "获取自定义板块列表"),
            ("get_trading_calendar.py", "获取交易日历"),
            ("get_trading_dates.py", "获取交易日列表"),
            ("refresh_cache.py", "刷新市场缓存"),
            ("refresh_kline.py", "刷新证券 K 线缓存"),
            ("subscribe_hq.py", "订阅实时行情"),
            ("unsubscribe_hq.py", "取消行情订阅"),
            ("get_subscribe_hq_stock_list.py", "获取原始订阅列表"),
            ("get_subscribe_hq_stock_list_cached.py", "获取带缓存回退的订阅列表"),
            ("subscribe_quote.py", "订阅 K 线/分笔推送"),
            ("get_trackzs_etf_info.py", "获取指数跟踪 ETF 列表"),
        ],
    ),
    (
        "扩展资料",
        [
            ("get_more_info.py", "获取证券扩展字段"),
            ("get_relation.py", "获取证券所属板块关系"),
            ("get_pricevol.py", "获取价量快照"),
            ("get_divid_factors.py", "获取分红送转数据"),
            ("get_financial_data.py", "获取财务数据"),
            ("get_financial_data_by_date.py", "按报告期获取财务数据"),
            ("get_gb_info.py", "获取股本信息"),
            ("get_gb_info_by_date.py", "按日期区间获取股本信息"),
            ("get_kzz_info.py", "获取可转债信息"),
            ("get_ipo_info.py", "获取新股新债申购信息"),
            ("get_match_stkinfo.py", "按关键字匹配证券"),
            ("get_gp_one_data.py", "获取个股单项数据"),
            ("get_gpjy_value.py", "获取股票交易数据"),
            ("get_gpjy_value_by_date.py", "按日期获取股票交易数据"),
            ("get_bkjy_value.py", "获取板块交易数据"),
            ("get_bkjy_value_by_date.py", "按日期获取板块交易数据"),
            ("get_scjy_value.py", "获取市场交易数据"),
            ("get_scjy_value_by_date.py", "按日期获取市场交易数据"),
        ],
    ),
    (
        "客户端操作",
        [
            ("create_sector.py", "创建自定义板块"),
            ("delete_sector.py", "删除自定义板块"),
            ("rename_sector.py", "重命名自定义板块"),
            ("clear_sector.py", "清空自定义板块"),
            ("download_file.py", "下载客户端文件"),
            ("send_message.py", "发送客户端消息"),
            ("send_file.py", "发送文件到客户端"),
            ("send_warn.py", "发送预警信号"),
            ("send_bt_data.py", "发送回测数据"),
            ("send_user_block.py", "推送股票到自定义板块"),
            ("print_to_tdx.py", "导入表格到通达信目录"),
            ("exec_to_tdx.py", "让客户端执行内置动作"),
        ],
    ),
    (
        "公式接口",
        [
            ("formula_format_data.py", "格式化公式输入数据"),
            ("formula_set_data.py", "写入公式数据"),
            ("formula_set_data_info.py", "写入公式数据信息"),
            ("formula_get_data.py", "读取当前公式数据"),
            ("formula_zb.py", "执行指标公式"),
            ("formula_xg.py", "执行选股公式"),
            ("formula_exp.py", "执行表达式公式"),
            ("formula_process_mul_zb.py", "批量执行指标公式"),
            ("formula_process_mul_xg.py", "批量执行选股公式"),
            ("formula_process_mul_exp.py", "批量执行表达式公式"),
            ("formula_get_all.py", "获取公式列表"),
            ("formula_get_info.py", "获取公式详情"),
        ],
    ),
]


def _build_registry() -> tuple[list[CommandSpec], dict[str, CommandSpec]]:
    specs: list[CommandSpec] = []
    aliases: dict[str, CommandSpec] = {}
    for category, items in CATEGORY_SPECS:
        for script_name, summary in items:
            spec = CommandSpec(script_name=script_name, category=category, summary=summary)
            specs.append(spec)
            aliases[spec.command_name] = spec
            aliases[Path(script_name).stem] = spec
    return specs, aliases


COMMAND_SPECS, COMMAND_ALIASES = _build_registry()


def _program_label() -> str:
    env_label = os.environ.get(PROGRAM_LABEL_ENV_VAR, "").strip()
    if env_label:
        return env_label
    program_path = Path(sys.argv[0])
    if program_path.parent.name == SCRIPTS_PACKAGE_NAME:
        return f"{SCRIPTS_PACKAGE_NAME}/{program_path.name}"
    return program_path.name


def _scripts_dir() -> Path:
    package = importlib.import_module(SCRIPTS_PACKAGE_NAME)
    package_file = getattr(package, "__file__", None)
    if not package_file:
        raise RuntimeError("无法定位 scripts 包路径")
    return Path(package_file).resolve().parent


@contextmanager
def _script_runtime(spec: CommandSpec, args: list[str]):
    original_argv = sys.argv[:]
    scripts_dir = _scripts_dir()
    scripts_dir_str = str(scripts_dir)
    inserted = False
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)
        inserted = True
    sys.argv = [str(scripts_dir / spec.script_name), *args]
    try:
        yield
    finally:
        sys.argv = original_argv
        if inserted:
            try:
                sys.path.remove(scripts_dir_str)
            except ValueError:
                pass


def _render_help() -> str:
    lines = [
        "通达信基础接口统一命令入口",
        "",
        "用法:",
        f"  {_program_label()} <command> [args]",
        f"  {_program_label()} help <command>",
        "",
        "说明:",
        "  - 这里只收基础接口命令，不包含组合模块命令",
        "  - 现有 scripts/*.py 入口继续保留",
        "  - `<command>` 同时支持 `get-market-data` 和 `get_market_data` 两种写法",
        "",
        "可用命令:",
    ]
    for category, _ in CATEGORY_SPECS:
        lines.append(f"  [{category}]")
        for spec in COMMAND_SPECS:
            if spec.category != category:
                continue
            lines.append(f"    {spec.command_name:<32} {spec.summary}")
    lines.append("")
    lines.append("查看子命令帮助示例:")
    lines.append(f"  {_program_label()} get-market-data --help")
    return "\n".join(lines)


def _run_script(spec: CommandSpec, args: list[str]) -> int:
    with _script_runtime(spec, args):
        try:
            runpy.run_module(spec.module_name, run_name="__main__")
            return 0
        except SystemExit as exc:
            if isinstance(exc.code, int):
                return exc.code
            if exc.code is None:
                return 0
            return 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print(_render_help())
        return 0

    if args[0] == "help":
        if len(args) == 1:
            print(_render_help())
            return 0
        spec = COMMAND_ALIASES.get(args[1])
        if spec is None:
            print(f"未知命令: {args[1]}", file=sys.stderr)
            print(_render_help(), file=sys.stderr)
            return 2
        return _run_script(spec, ["--help"])

    spec = COMMAND_ALIASES.get(args[0])
    if spec is None:
        print(f"未知命令: {args[0]}", file=sys.stderr)
        print(_render_help(), file=sys.stderr)
        return 2

    return _run_script(spec, args[1:])


def invoke(argv: list[str] | None = None, *, program_label: str | None = None) -> int:
    original_label = os.environ.get(PROGRAM_LABEL_ENV_VAR)
    try:
        if program_label:
            os.environ[PROGRAM_LABEL_ENV_VAR] = program_label
        return main(argv)
    finally:
        if original_label is None:
            os.environ.pop(PROGRAM_LABEL_ENV_VAR, None)
        else:
            os.environ[PROGRAM_LABEL_ENV_VAR] = original_label


def console_main() -> int:
    return invoke(sys.argv[1:], program_label="tdx")
