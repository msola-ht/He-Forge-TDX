from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time

from lib.cli.runtime import add_output_argument, print_output


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class SmokeCommand:
    """A single real-TQ smoke command executed through the unified CLI."""

    name: str
    category: str
    args: list[str]
    mutating: bool = False
    require_nonempty_json: bool = False


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the real-TQ smoke runner."""
    parser = argparse.ArgumentParser(
        description="顺序执行一组真实 TQ 基础命令，用于本机连通性与基础接口冒烟验证",
    )
    parser.add_argument("--stock_code", default="000001.SZ", help="默认证券代码，默认 000001.SZ")
    parser.add_argument("--market", default="5", help="默认市场/分类代码，默认 5")
    parser.add_argument("--list_type", default="1", help="股票列表分类，默认 1")
    parser.add_argument(
        "--sector_block_code",
        default="881001.SH",
        help="板块成分与板块交易数据使用的系统板块代码，默认 881001.SH",
    )
    parser.add_argument("--calendar_market", default="SH", help="交易日历市场，默认 SH")
    parser.add_argument("--start_time", default="20260601", help="默认开始日期，格式 YYYYMMDD")
    parser.add_argument("--end_time", default="20260630", help="默认结束日期，格式 YYYYMMDD")
    parser.add_argument("--gb_date", default="20250624", help="股本信息测试日期，格式 YYYYMMDD")
    parser.add_argument(
        "--stock_info_fields",
        nargs="+",
        default=["Name", "Unit"],
        help="get-stock-info 使用的字段列表，默认 Name Unit",
    )
    parser.add_argument(
        "--trackzs_code",
        default="950162.CSI",
        help="指数跟踪 ETF 测试用指数代码，默认 950162.CSI",
    )
    parser.add_argument(
        "--kzz_stock_code",
        default="",
        help="可转债测试代码；留空时自动调用 market=32 股票列表取第一只",
    )
    parser.add_argument("--formula_name", default="MACD", help="默认公式名称，默认 MACD")
    parser.add_argument("--formula_arg", default="12,26,9", help="默认公式参数，默认 12,26,9")
    parser.add_argument("--prepare_count", default="120", help="公式预载 K 线数量，默认 120")
    parser.add_argument(
        "--include-write-ops",
        action="store_true",
        help="额外执行订阅、自定义板块、消息发送、公式写入等带副作用的命令",
    )
    parser.add_argument(
        "--write_block_code",
        default="TST001",
        help="当 include-write-ops=true 时使用的临时自定义板块代码，默认 TST001",
    )
    parser.add_argument(
        "--write_block_name",
        default="Codex基础验证",
        help="当 include-write-ops=true 时使用的临时自定义板块名称",
    )
    parser.add_argument(
        "--fail_fast",
        action="store_true",
        help="任一命令失败后立即停止，默认继续执行剩余命令",
    )
    parser.add_argument(
        "--show_output",
        action="store_true",
        help="在结果中附带 stdout/stderr 摘要，便于直接定位问题",
    )
    add_output_argument(parser)
    return parser


def _command(
    name: str,
    category: str,
    *args: str,
    mutating: bool = False,
    require_nonempty_json: bool = False,
) -> SmokeCommand:
    return SmokeCommand(
        name=name,
        category=category,
        args=list(args),
        mutating=mutating,
        require_nonempty_json=require_nonempty_json,
    )


def _decode_output(value: bytes | str | None) -> str:
    """Decode subprocess output robustly across mixed Windows console encodings."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value

    candidates = ["utf-8", "utf-8-sig", sys.getdefaultencoding(), "gbk", "cp936"]
    tried: set[str] = set()
    for encoding in candidates:
        normalized = encoding.lower()
        if normalized in tried:
            continue
        tried.add(normalized)
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue
        except LookupError:
            continue

    return value.decode("utf-8", errors="replace")


def _summarize_output(stdout: str, stderr: str, returncode: int) -> str:
    stdout = stdout.strip()
    stderr = stderr.strip()
    if returncode != 0:
        if stderr:
            return stderr.splitlines()[-1][:200]
        if stdout:
            return stdout.splitlines()[-1][:200]
        return "command failed"

    if not stdout:
        return "ok"

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout.splitlines()[0][:200]

    if isinstance(data, list):
        return f"list[{len(data)}]"
    if isinstance(data, dict):
        keys = list(data.keys())[:5]
        return f"dict keys={keys}"
    return type(data).__name__


def _run_cli_command(command_args: list[str]) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return subprocess.run(
        [sys.executable, "tdx.py", *command_args],
        cwd=ROOT,
        capture_output=True,
        text=False,
        check=False,
        env=env,
    )


def _build_result(
    *,
    name: str,
    category: str,
    mutating: bool,
    returncode: int,
    seconds: float,
    command: str,
    stdout: str = "",
    stderr: str = "",
    show_output: bool = False,
) -> dict:
    result = {
        "name": name,
        "category": category,
        "mutating": mutating,
        "ok": returncode == 0,
        "returncode": returncode,
        "seconds": seconds,
        "command": command,
        "summary": _summarize_output(stdout, stderr, returncode),
    }
    if show_output:
        result["stdout"] = stdout.strip()[:1000]
        result["stderr"] = stderr.strip()[:1000]
    return result


def _has_meaningful_json(stdout: str) -> bool:
    """Return whether a JSON payload is non-empty enough to count as a real result."""
    payload = stdout.strip()
    if not payload:
        return False

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return True

    if isinstance(data, dict):
        return bool(data)
    if isinstance(data, list):
        return bool(data)
    return True


def _discover_kzz_stock_code(preferred: str, *, show_output: bool) -> tuple[str | None, dict]:
    if preferred.strip():
        return preferred.strip(), {
            "name": "discover-kzz-stock-code",
            "category": "预处理",
            "mutating": False,
            "ok": True,
            "returncode": 0,
            "seconds": 0.0,
            "command": f"manual kzz_stock_code={preferred.strip()}",
            "summary": preferred.strip(),
        }

    started = time.perf_counter()
    completed = _run_cli_command(
        [
            "get-stock-list",
            "--market",
            "32",
            "--list_type",
            "1",
            "--output",
            "json",
        ]
    )
    elapsed = round(time.perf_counter() - started, 3)
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    command = "python tdx.py get-stock-list --market 32 --list_type 1 --output json"

    if completed.returncode != 0:
        return None, _build_result(
            name="discover-kzz-stock-code",
            category="预处理",
            mutating=False,
            returncode=completed.returncode,
            seconds=elapsed,
            command=command,
            stdout=stdout,
            stderr=stderr,
            show_output=show_output,
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return None, {
            "name": "discover-kzz-stock-code",
            "category": "预处理",
            "mutating": False,
            "ok": False,
            "returncode": 1,
            "seconds": elapsed,
            "command": command,
            "summary": f"JSON 解析失败: {exc}",
            **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
        }

    if not isinstance(data, list) or not data:
        return None, {
            "name": "discover-kzz-stock-code",
            "category": "预处理",
            "mutating": False,
            "ok": False,
            "returncode": 1,
            "seconds": elapsed,
            "command": command,
            "summary": "market=32 未返回可用可转债代码",
            **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
        }

    first = data[0]
    if isinstance(first, dict):
        code = first.get("Code", "")
    else:
        code = str(first)
    code = str(code).strip()
    if not code:
        return None, {
            "name": "discover-kzz-stock-code",
            "category": "预处理",
            "mutating": False,
            "ok": False,
            "returncode": 1,
            "seconds": elapsed,
            "command": command,
            "summary": "无法从 market=32 结果中解析可转债代码",
            **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
        }

    return code, {
        "name": "discover-kzz-stock-code",
        "category": "预处理",
        "mutating": False,
        "ok": True,
        "returncode": 0,
        "seconds": elapsed,
        "command": command,
        "summary": code,
        **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
    }


def _prepare_formula_data_file(args: argparse.Namespace, *, show_output: bool) -> tuple[str | None, dict]:
    command_args = [
        "formula-format-data",
        "--stock_list",
        args.stock_code,
        "--period",
        "1d",
        "--count",
        str(args.prepare_count),
        "--output",
        "json",
    ]
    started = time.perf_counter()
    completed = _run_cli_command(command_args)
    elapsed = round(time.perf_counter() - started, 3)
    stdout = _decode_output(completed.stdout)
    stderr = _decode_output(completed.stderr)
    command = f"python tdx.py {shlex.join(command_args)}"

    if completed.returncode != 0:
        return None, _build_result(
            name="formula-format-data",
            category="预处理",
            mutating=False,
            returncode=completed.returncode,
            seconds=elapsed,
            command=command,
            stdout=stdout,
            stderr=stderr,
            show_output=show_output,
        )

    try:
        json.loads(stdout)
    except json.JSONDecodeError as exc:
        return None, {
            "name": "formula-format-data",
            "category": "预处理",
            "mutating": False,
            "ok": False,
            "returncode": 1,
            "seconds": elapsed,
            "command": command,
            "summary": f"JSON 解析失败: {exc}",
            **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
        }

    temp_dir = Path(tempfile.gettempdir()) / "tdx_basic_tq_smoke"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / f"formula_format_{args.stock_code.replace('.', '_')}.json"
    temp_file.write_text(stdout, encoding="utf-8")
    return str(temp_file), {
        "name": "formula-format-data",
        "category": "预处理",
        "mutating": False,
        "ok": True,
        "returncode": 0,
        "seconds": elapsed,
        "command": command,
        "summary": f"prepared {temp_file}",
        **({"stdout": stdout[:1000], "stderr": stderr[:1000]} if show_output else {}),
    }


def build_commands(
    args: argparse.Namespace,
    *,
    kzz_stock_code: str | None,
    formula_data_file: str | None,
) -> list[SmokeCommand]:
    """Build the smoke command list from CLI arguments."""
    commands = [
        _command(
            "diagnose-tdx-path",
            "路径与诊断",
            "diagnose-tdx-path",
            "--probe",
            "stock_list",
            "--market",
            args.market,
            "--output",
            "json",
        ),
        _command(
            "get-stock-list",
            "行情与市场",
            "get-stock-list",
            "--market",
            args.market,
            "--list_type",
            args.list_type,
            "--output",
            "json",
        ),
        _command(
            "get-stock-info",
            "行情与市场",
            "get-stock-info",
            "--stock_code",
            args.stock_code,
            "--field_list",
            *args.stock_info_fields,
            "--output",
            "json",
        ),
        _command(
            "get-market-snapshot",
            "行情与市场",
            "get-market-snapshot",
            "--stock_code",
            args.stock_code,
            "--field_list",
            "Now",
            "LastClose",
            "Open",
            "--output",
            "json",
        ),
        _command(
            "get-market-data",
            "行情与市场",
            "get-market-data",
            "--stock_list",
            args.stock_code,
            "--period",
            "1d",
            "--count",
            "5",
            "--output",
            "json",
        ),
        _command("get-sector-list", "行情与市场", "get-sector-list", "--list_type", "1", "--output", "json"),
        _command(
            "get-stock-list-in-sector",
            "行情与市场",
            "get-stock-list-in-sector",
            "--block_code",
            args.sector_block_code,
            "--output",
            "json",
        ),
        _command("get-user-sector", "行情与市场", "get-user-sector", "--output", "json"),
        _command(
            "get-trading-calendar",
            "行情与市场",
            "get-trading-calendar",
            "--market",
            args.calendar_market,
            "--start_time",
            args.start_time,
            "--end_time",
            args.end_time,
            "--output",
            "json",
        ),
        _command(
            "get-trading-dates",
            "行情与市场",
            "get-trading-dates",
            "--market",
            args.calendar_market,
            "--start_time",
            args.start_time,
            "--end_time",
            args.end_time,
            "--output",
            "json",
        ),
        _command(
            "get-trackzs-etf-info",
            "行情与市场",
            "get-trackzs-etf-info",
            "--zs_code",
            args.trackzs_code,
            "--output",
            "json",
            require_nonempty_json=True,
        ),
        _command(
            "get-more-info",
            "扩展资料",
            "get-more-info",
            "--stock_code",
            args.stock_code,
            "--field_list",
            "Name",
            "Zjl",
            "--output",
            "json",
        ),
        _command(
            "get-relation",
            "扩展资料",
            "get-relation",
            "--stock_code",
            args.stock_code,
            "--output",
            "json",
        ),
        _command(
            "get-divid-factors",
            "扩展资料",
            "get-divid-factors",
            "--stock_code",
            args.stock_code,
            "--output",
            "json",
        ),
        _command(
            "get-financial-data",
            "扩展资料",
            "get-financial-data",
            "--stock_list",
            args.stock_code,
            "--field_list",
            "FN1",
            "FN8",
            "FN134",
            "--output",
            "json",
        ),
        _command(
            "get-gb-info",
            "扩展资料",
            "get-gb-info",
            "--stock_code",
            args.stock_code,
            "--date_list",
            args.gb_date,
            "--output",
            "json",
        ),
    ]

    if kzz_stock_code:
        commands.append(
            _command(
                "get-kzz-info",
                "扩展资料",
                "get-kzz-info",
                "--stock_code",
                kzz_stock_code,
                "--output",
                "json",
            )
        )

    commands.extend(
        [
            _command("get-ipo-info", "扩展资料", "get-ipo-info", "--output", "json"),
            _command(
                "get-subscribe-hq-stock-list-cached",
                "客户端操作",
                "get-subscribe-hq-stock-list-cached",
                "--output",
                "json",
            ),
            _command("formula-get-all", "公式接口", "formula-get-all", "--output", "json"),
            _command(
                "formula-get-info",
                "公式接口",
                "formula-get-info",
                "--formula_code",
                args.formula_name,
                "--output",
                "json",
            ),
            _command(
                "formula-zb",
                "公式接口",
                "formula-zb",
                "--formula_name",
                args.formula_name,
                "--formula_arg",
                args.formula_arg,
                "--prepare_stock_code",
                args.stock_code,
                "--prepare_stock_period",
                "1d",
                "--prepare_count",
                args.prepare_count,
                "--output",
                "json",
            ),
            _command(
                "formula-exp",
                "公式接口",
                "formula-exp",
                "--formula_name",
                args.formula_name,
                "--formula_arg",
                args.formula_arg,
                "--prepare_stock_code",
                args.stock_code,
                "--prepare_stock_period",
                "1d",
                "--prepare_count",
                args.prepare_count,
                "--output",
                "json",
            ),
            _command(
                "formula-get-data",
                "公式接口",
                "formula-get-data",
                "--formula_kind",
                "exp",
                "--formula_name",
                args.formula_name,
                "--formula_arg",
                args.formula_arg,
                "--prepare_stock_code",
                args.stock_code,
                "--prepare_stock_period",
                "1d",
                "--prepare_count",
                args.prepare_count,
                "--output",
                "json",
            ),
        ]
    )

    if args.include_write_ops:
        commands.extend(
            [
                _command(
                    "subscribe-hq",
                    "写操作",
                    "subscribe-hq",
                    "--stock_list",
                    args.stock_code,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "unsubscribe-hq",
                    "写操作",
                    "unsubscribe-hq",
                    "--stock_list",
                    args.stock_code,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "create-sector",
                    "写操作",
                    "create-sector",
                    "--block_code",
                    args.write_block_code,
                    "--block_name",
                    args.write_block_name,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "send-user-block",
                    "写操作",
                    "send-user-block",
                    "--block_code",
                    args.write_block_code,
                    "--stocks",
                    args.stock_code,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "clear-sector",
                    "写操作",
                    "clear-sector",
                    "--block_code",
                    args.write_block_code,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "delete-sector",
                    "写操作",
                    "delete-sector",
                    "--block_code",
                    args.write_block_code,
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "send-message",
                    "写操作",
                    "send-message",
                    "--msg_str",
                    f"MSG,Codex基础验证|{args.stock_code}",
                    "--output",
                    "json",
                    mutating=True,
                ),
                _command(
                    "formula-set-data-info",
                    "写操作",
                    "formula-set-data-info",
                    "--stock_code",
                    args.stock_code,
                    "--stock_period",
                    "1d",
                    "--count",
                    "10",
                    "--output",
                    "json",
                    mutating=True,
                ),
            ]
        )

        if formula_data_file:
            commands.append(
                _command(
                    "formula-set-data",
                    "写操作",
                    "formula-set-data",
                    "--stock_code",
                    args.stock_code,
                    "--stock_period",
                    "1d",
                    "--stock_data_file",
                    formula_data_file,
                    "--count",
                    "10",
                    "--output",
                    "json",
                    mutating=True,
                )
            )

    return commands


def run_smoke(args: argparse.Namespace) -> dict:
    """Run the selected real-TQ smoke commands and return a structured summary."""
    results: list[dict] = []
    failed = 0

    kzz_stock_code, kzz_result = _discover_kzz_stock_code(args.kzz_stock_code, show_output=args.show_output)
    results.append(kzz_result)
    if not kzz_result["ok"]:
        failed += 1

    formula_data_file = None
    if args.include_write_ops:
        formula_data_file, formula_data_result = _prepare_formula_data_file(args, show_output=args.show_output)
        results.append(formula_data_result)
        if not formula_data_result["ok"]:
            failed += 1

    commands = build_commands(args, kzz_stock_code=kzz_stock_code, formula_data_file=formula_data_file)

    for item in commands:
        started = time.perf_counter()
        completed = _run_cli_command(item.args)
        stdout = _decode_output(completed.stdout)
        stderr = _decode_output(completed.stderr)
        elapsed = round(time.perf_counter() - started, 3)
        result = _build_result(
            name=item.name,
            category=item.category,
            mutating=item.mutating,
            returncode=completed.returncode,
            seconds=elapsed,
            command=f"python tdx.py {shlex.join(item.args)}",
            stdout=stdout,
            stderr=stderr,
            show_output=args.show_output,
        )
        if result["ok"] and item.require_nonempty_json and not _has_meaningful_json(stdout):
            result["ok"] = False
            result["returncode"] = 1
            result["summary"] = "empty JSON result"
            failed += 1
        elif not result["ok"]:
            failed += 1
        results.append(result)
        if not result["ok"] and args.fail_fast:
            break

    return {
        "summary": {
            "command_count": len(results),
            "failed_count": failed,
            "passed_count": len(results) - failed,
            "include_write_ops": bool(args.include_write_ops),
            "fail_fast": bool(args.fail_fast),
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the real-TQ smoke runner."""
    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_smoke(args)
    print_output(report, args.output)
    return 0 if report["summary"]["failed_count"] == 0 else 1
