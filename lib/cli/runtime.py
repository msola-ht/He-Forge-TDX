from __future__ import annotations

import json
from contextlib import contextmanager, redirect_stdout
from datetime import date, datetime
import os
from pathlib import Path
import shutil
import sys
import unicodedata

import numpy as np
import pandas as pd

from lib.tqcenter import tq

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUBSCRIBE_STATE_FILE = ROOT / "lib" / "tdx_subscribe_state.json"
SUBSCRIBE_STATE_FILE_ENV_VAR = "TDX_SUBSCRIBE_STATE_FILE"
SUBSCRIBE_STATE_FILE = DEFAULT_SUBSCRIBE_STATE_FILE
DEFAULT_TQ_PREFLIGHT_MARKET = "5"
DEFAULT_TQ_PREFLIGHT_LIST_TYPE = 1


def resolve_subscribe_state_file() -> Path:
    configured = os.environ.get(SUBSCRIBE_STATE_FILE_ENV_VAR, "").strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_SUBSCRIBE_STATE_FILE


def initialize_tq(entry_file: str):
    tq.initialize(entry_file)
    return tq


def _build_tq_preflight_guidance() -> str:
    return (
        "请先运行 `python scripts/diagnose_tdx_path.py --probe stock_list --market 5 --output json` "
        "检查当前机器上的通达信路径、登录状态与基础行情连通性。"
        "如果仍不通过，再运行 `python scripts/setup_tdx_path.py --show-all --output json` "
        "选择并保存可用通达信客户端路径。"
    )


def probe_tq_connectivity(
    tq_obj,
    *,
    market: str = DEFAULT_TQ_PREFLIGHT_MARKET,
    list_type: int = DEFAULT_TQ_PREFLIGHT_LIST_TYPE,
) -> dict:
    """使用 get_stock_list 做一次通用连通性探测。"""
    try:
        data = tq_obj.get_stock_list(
            market=market,
            list_type=list_type,
        )
    except Exception as exc:
        raise RuntimeError(
            "TQ 连通性检测失败: "
            f"调用 get_stock_list(market={market}, list_type={list_type}) 抛出 {type(exc).__name__}: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise RuntimeError(
            "TQ 连通性检测失败: "
            f"get_stock_list(market={market}, list_type={list_type}) 返回了 {type(data).__name__}，不是列表"
        )

    if not data:
        raise RuntimeError(
            "TQ 连通性检测失败: "
            f"get_stock_list(market={market}, list_type={list_type}) 返回空结果。"
            + _build_tq_preflight_guidance()
        )

    return {
        "probe": "stock_list",
        "market": str(market),
        "list_type": int(list_type),
        "count": len(data),
        "sample": data[:3],
    }


def ensure_tq_ready(
    tq_obj,
    *,
    preflight: bool = True,
    preflight_callback=None,
) -> dict | None:
    """在正式调用前执行一次通用连通性探测，并允许功能模块追加自定义探测。"""
    if not preflight:
        return None

    result = {
        "connectivity": probe_tq_connectivity(tq_obj),
    }
    if preflight_callback is not None:
        result["feature_probe"] = preflight_callback(tq_obj)
    return result


def run_tq_call(entry_file: str, callback, *, preflight: bool = True, preflight_callback=None):
    with redirect_stdout(sys.stderr):
        tq.initialize(entry_file)
        try:
            ensure_tq_ready(
                tq,
                preflight=preflight,
                preflight_callback=preflight_callback,
            )
            return callback(tq)
        finally:
            tq.close()


@contextmanager
def tq_session(entry_file: str, *, preflight: bool = True, preflight_callback=None):
    with redirect_stdout(sys.stderr):
        tq.initialize(entry_file)
        try:
            ensure_tq_ready(
                tq,
                preflight=preflight,
                preflight_callback=preflight_callback,
            )
            yield tq
        finally:
            tq.close()


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"无法解析布尔值: {value}")


def add_output_argument(parser) -> None:
    parser.add_argument(
        "--output",
        default="raw",
        choices=["raw", "json", "table"],
        help="输出格式: raw=原始输出(默认), table=Markdown表格输出, json=结构化输出",
    )


def _to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(item) for item in value]

    if isinstance(value, pd.DataFrame):
        frame = value.astype(object).where(pd.notna(value), None)
        return {
            str(index): {
                str(column): _to_jsonable(cell)
                for column, cell in row.items()
            }
            for index, row in frame.iterrows()
        }

    if isinstance(value, pd.Series):
        series = value.astype(object).where(pd.notna(value), None)
        return {str(index): _to_jsonable(item) for index, item in series.items()}

    if isinstance(value, np.ndarray):
        return [_to_jsonable(item) for item in value.tolist()]

    if isinstance(value, np.generic):
        return _to_jsonable(value.item())

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()

    if value is pd.NA or pd.isna(value):
        return None

    return value


def print_json(value) -> None:
    print(
        json.dumps(
            _to_jsonable(value),
            ensure_ascii=False,
            indent=2,
        )
    )


def _markdown_cell(value) -> str:
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)

    return text.replace("|", "\\|").replace("\n", "<br>")


def _char_display_width(char: str) -> int:
    if not char:
        return 0
    if unicodedata.combining(char):
        return 0
    if unicodedata.east_asian_width(char) in {"F", "W"}:
        return 2
    return 1


def _display_width(text: str) -> int:
    return sum(_char_display_width(char) for char in str(text))


def _truncate_display_width(text: str, max_width: int) -> str:
    rendered = str(text)
    if max_width <= 0:
        return ""
    if _display_width(rendered) <= max_width:
        return rendered
    if max_width <= 3:
        return "." * max_width

    target_width = max_width - 3
    current_width = 0
    result = []
    for char in rendered:
        char_width = _char_display_width(char)
        if current_width + char_width > target_width:
            break
        result.append(char)
        current_width += char_width
    return "".join(result).rstrip() + "..."


def _pad_display_width(text: str, width: int) -> str:
    rendered = _truncate_display_width(text, width)
    padding = max(0, width - _display_width(rendered))
    return rendered + (" " * padding)


def _resolve_table_max_width() -> int:
    value = os.environ.get("TQ_TABLE_MAX_WIDTH", "").strip()
    if value:
        try:
            parsed = int(value)
        except ValueError:
            parsed = 0
        if parsed > 0:
            return parsed
    return shutil.get_terminal_size(fallback=(120, 20)).columns


def _fit_markdown_column_widths(rendered_columns: list[str], rendered_rows: list[list[str]]) -> list[int]:
    widths = []
    for idx, header in enumerate(rendered_columns):
        row_widths = [_display_width(row[idx]) for row in rendered_rows] if rendered_rows else []
        widths.append(max(_display_width(header), *row_widths, 3))

    max_total_width = max(_resolve_table_max_width(), 20)
    total_width = sum(widths) + (3 * len(widths)) + 1
    if total_width <= max_total_width:
        return widths

    min_widths = [min(width, max(3, min(_display_width(header), 12))) for width, header in zip(widths, rendered_columns)]
    while total_width > max_total_width:
        shrinkable_indexes = [idx for idx, width in enumerate(widths) if width > min_widths[idx]]
        if not shrinkable_indexes:
            break
        target_idx = max(shrinkable_indexes, key=lambda idx: widths[idx])
        widths[target_idx] -= 1
        total_width -= 1

    return widths


def _natural_markdown_widths(rendered_columns: list[str], rendered_rows: list[list[str]]) -> list[int]:
    widths = []
    for idx, header in enumerate(rendered_columns):
        row_widths = [_display_width(row[idx]) for row in rendered_rows] if rendered_rows else []
        widths.append(max(_display_width(header), *row_widths, 3))
    return widths


def _render_markdown_table(rendered_columns: list[str], rendered_rows: list[list[str]]) -> str:
    column_widths = _fit_markdown_column_widths(rendered_columns, rendered_rows)

    def _render_row(row: list[str]) -> str:
        padded = [_pad_display_width(cell, column_widths[idx]) for idx, cell in enumerate(row)]
        return "| " + " | ".join(padded) + " |"

    header = _render_row(rendered_columns)
    separator = "| " + " | ".join("-" * max(3, width) for width in column_widths) + " |"

    if not rendered_rows:
        return "\n".join([header, separator])

    body = [_render_row(row) for row in rendered_rows]
    return "\n".join([header, separator, *body])


def _split_markdown_table_columns(rendered_columns: list[str], rendered_rows: list[list[str]]) -> list[list[int]]:
    if len(rendered_columns) <= 6:
        return [list(range(len(rendered_columns)))]

    natural_widths = _natural_markdown_widths(rendered_columns, rendered_rows)
    max_total_width = max(_resolve_table_max_width(), 20)
    natural_total_width = sum(natural_widths) + (3 * len(natural_widths)) + 1
    if natural_total_width <= max_total_width:
        return [list(range(len(rendered_columns)))]

    anchor_count = 2 if len(rendered_columns) >= 4 else 1
    anchor_indexes = list(range(anchor_count))
    chunks: list[list[int]] = []
    current_chunk = anchor_indexes.copy()
    current_width = sum(natural_widths[idx] for idx in current_chunk) + (3 * len(current_chunk)) + 1

    for idx in range(anchor_count, len(rendered_columns)):
        candidate_width = current_width + natural_widths[idx] + 3
        if len(current_chunk) > anchor_count and candidate_width > max_total_width:
            chunks.append(current_chunk)
            current_chunk = anchor_indexes.copy() + [idx]
            current_width = sum(natural_widths[item] for item in current_chunk) + (3 * len(current_chunk)) + 1
            continue
        current_chunk.append(idx)
        current_width = candidate_width

    if current_chunk:
        chunks.append(current_chunk)

    if len(chunks) <= 1:
        return [list(range(len(rendered_columns)))]
    return chunks


def _markdown_table(frame: pd.DataFrame, include_index: bool = False) -> str:
    frame = frame.astype(object).where(pd.notna(frame), None)

    if include_index:
        rows = []
        index_name = frame.index.name or "index"
        columns = [index_name, *[str(column) for column in frame.columns]]
        for index, row in frame.iterrows():
            rows.append([index, *row.tolist()])
    else:
        columns = [str(column) for column in frame.columns]
        rows = [row.tolist() for _, row in frame.iterrows()]

    rendered_columns = [_markdown_cell(column) for column in columns]
    rendered_rows = [[_markdown_cell(cell) for cell in row] for row in rows]
    column_chunks = _split_markdown_table_columns(rendered_columns, rendered_rows)
    parts = []
    for chunk_indexes in column_chunks:
        chunk_columns = [rendered_columns[idx] for idx in chunk_indexes]
        chunk_rows = [[row[idx] for idx in chunk_indexes] for row in rendered_rows]
        parts.append(_render_markdown_table(chunk_columns, chunk_rows))
    return "\n\n".join(parts)


def _format_table(value) -> str:
    if isinstance(value, pd.DataFrame):
        return _markdown_table(value)

    if isinstance(value, pd.Series):
        frame = pd.DataFrame(
            [{"field": index, "value": item} for index, item in value.items()]
        )
        return _markdown_table(frame)

    if isinstance(value, dict):
        if not value:
            return "(empty)"

        if all(isinstance(item, pd.DataFrame) for item in value.values()):
            parts = []
            for key, frame in value.items():
                parts.append(f"[{key}]")
                parts.append(_format_table(frame))
            return "\n\n".join(parts)

        jsonable = _to_jsonable(value)
        if all(not isinstance(item, (dict, list)) for item in jsonable.values()):
            frame = pd.DataFrame(
                [{"field": key, "value": item} for key, item in jsonable.items()]
            )
            return _markdown_table(frame)

        if all(isinstance(item, dict) for item in jsonable.values()):
            if all(
                all(not isinstance(sub_item, (dict, list)) for sub_item in item.values())
                for item in jsonable.values()
            ):
                frame = pd.DataFrame.from_dict(jsonable, orient="index")
                return _markdown_table(frame, include_index=True)

        parts = []
        scalar_items = {
            key: item
            for key, item in value.items()
            if not isinstance(_to_jsonable(item), (dict, list))
        }
        nested_items = {
            key: item
            for key, item in value.items()
            if isinstance(_to_jsonable(item), (dict, list))
        }

        if scalar_items:
            frame = pd.DataFrame(
                [{"field": key, "value": _to_jsonable(item)} for key, item in scalar_items.items()]
            )
            parts.append(_markdown_table(frame))

        for key, item in nested_items.items():
            if parts:
                parts.append("")
            parts.append(f"[{key}]")
            parts.append(_format_table(item))
        return "\n\n".join(parts)

    if isinstance(value, list):
        if not value:
            return "(empty)"

        jsonable = _to_jsonable(value)
        if all(isinstance(item, dict) for item in jsonable):
            return _markdown_table(pd.DataFrame(jsonable))

        return _markdown_table(pd.DataFrame({"value": jsonable}))

    return str(_to_jsonable(value))


def print_output(value, output: str) -> None:
    if output == "raw":
        print(value)
        return

    if output == "table":
        print(_format_table(value))
        return

    print_json(value)


def load_subscribe_state() -> list[str]:
    state_file = resolve_subscribe_state_file()
    if not state_file.exists():
        return []

    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item) for item in data]


def save_subscribe_state(codes: list[str]) -> None:
    unique_codes = sorted(set(codes))
    state_file = resolve_subscribe_state_file()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(unique_codes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def remember_subscriptions(codes: list[str]) -> None:
    current = set(load_subscribe_state())
    current.update(codes)
    save_subscribe_state(list(current))


def forget_subscriptions(codes: list[str]) -> None:
    removed = set(codes)
    current = [code for code in load_subscribe_state() if code not in removed]
    save_subscribe_state(current)


def send_user_block_compat(tq_obj, *, block_code: str, stocks: list[str], show: bool = False):
    """兼容不同 tqcenter 版本的 send_user_block 参数名差异。"""

    try:
        return tq_obj.send_user_block(
            block_code=block_code,
            stock_list=stocks,
            show=show,
        )
    except TypeError as exc:
        if "unexpected keyword argument 'stock_list'" not in str(exc):
            raise

    try:
        return tq_obj.send_user_block(
            block_code=block_code,
            stocks=stocks,
            show=show,
        )
    except TypeError as exc:
        if "unexpected keyword argument 'stocks'" not in str(exc):
            raise

    return tq_obj.send_user_block(block_code, stocks, show)
