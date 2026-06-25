import argparse
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from _bootstrap import add_output_argument, print_output, run_tq_call
from lib.config import describe_tdx_user_dir_candidates, find_tdx_user_dir, load_config
from lib.tqcenter import _load_external_module

parser = argparse.ArgumentParser(description="诊断通达信路径解析与基础连通性")
parser.add_argument(
    "--probe",
    default="stock_list",
    choices=["none", "stock_list", "market_snapshot"],
    help="可选探针: none=只诊断路径, stock_list=调用 get_stock_list, market_snapshot=调用 get_market_snapshot",
)
parser.add_argument(
    "--market",
    default="5",
    help="当 probe=stock_list 时使用的市场/分类代码，默认 5=所有A股",
)
parser.add_argument(
    "--stock_code",
    default="000001.SZ",
    help="当 probe=market_snapshot 时使用的证券代码，默认 000001.SZ",
)
parser.add_argument(
    "--show-candidates",
    action="store_true",
    help="显示完整候选路径列表；默认仅显示当前生效路径摘要",
)
add_output_argument(parser)

args = parser.parse_args()


SOURCE_PRIORITY = {
    "registry": 0,
    "config": 1,
    "env_tdx_user_dir": 2,
    "env_tdx_root": 3,
    "common_root": 4,
}


def _candidate_key(path: str) -> str:
    normalized = path.replace("\\", "/")
    if platform.system() == "Windows":
        return normalized.lower()
    return normalized


def _merge_candidates(groups: list[dict]) -> list[dict]:
    merged = {}
    for group in groups:
        for variant in group["variants"]:
            key = _candidate_key(variant["path"])
            item = merged.get(key)
            if item is None:
                item = {
                    "path": variant["path"],
                    "install_root": variant["install_root"],
                    "sources": [],
                    "details": [],
                    "user_dir_exists": variant["user_dir_exists"],
                    "tqcenter_exists": variant["tqcenter_exists"],
                    "plugin_dir_exists": variant["plugin_dir_exists"],
                    "tpythclient_exists": variant["tpythclient_exists"],
                    "tpyth_exists": variant["tpyth_exists"],
                    "tdxw_exists": variant["tdxw_exists"],
                    "is_mock_like": variant["is_mock_like"],
                    "is_valid_user_dir": variant["is_valid_user_dir"],
                    "source_priority": SOURCE_PRIORITY.get(group["source"], 99),
                }
                merged[key] = item
            else:
                item["user_dir_exists"] = item["user_dir_exists"] or variant["user_dir_exists"]
                item["tqcenter_exists"] = item["tqcenter_exists"] or variant["tqcenter_exists"]
                item["plugin_dir_exists"] = item["plugin_dir_exists"] or variant["plugin_dir_exists"]
                item["tpythclient_exists"] = item["tpythclient_exists"] or variant["tpythclient_exists"]
                item["tpyth_exists"] = item["tpyth_exists"] or variant["tpyth_exists"]
                item["tdxw_exists"] = item["tdxw_exists"] or variant["tdxw_exists"]
                item["is_mock_like"] = item["is_mock_like"] or variant["is_mock_like"]
                item["is_valid_user_dir"] = item["is_valid_user_dir"] or variant["is_valid_user_dir"]
                item["source_priority"] = min(
                    item["source_priority"],
                    SOURCE_PRIORITY.get(group["source"], 99),
                )

            if group["source"] not in item["sources"]:
                item["sources"].append(group["source"])
            if group["detail"] not in item["details"]:
                item["details"].append(group["detail"])

    return sorted(
        merged.values(),
        key=lambda item: (
            not item["is_valid_user_dir"],
            item["source_priority"],
            item["path"].lower() if platform.system() == "Windows" else item["path"],
        ),
    )


def _build_selected_summary(selected_user_dir: str | None, candidates: list[dict]) -> dict | None:
    if not selected_user_dir:
        return None

    selected_key = _candidate_key(selected_user_dir)
    matched = next((item for item in candidates if _candidate_key(item["path"]) == selected_key), None)
    if matched is None:
        return {
            "user_dir": selected_user_dir,
            "matched_candidate": False,
        }

    return {
        "user_dir": matched["path"],
        "install_root": matched["install_root"],
        "sources": matched["sources"],
        "details": matched["details"],
        "is_valid_user_dir": matched["is_valid_user_dir"],
        "tqcenter_exists": matched["tqcenter_exists"],
        "tpythclient_exists": matched["tpythclient_exists"],
        "tdxw_exists": matched["tdxw_exists"],
        "is_mock_like": matched["is_mock_like"],
        "matched_candidate": True,
    }


def _run_probe():
    if args.probe == "none":
        return {"status": "skipped"}

    if args.probe == "stock_list":
        data = run_tq_call(
            __file__,
            lambda tq: tq.get_stock_list(market=args.market, list_type=1),
            preflight=False,
        )
        summary = {
            "status": "ok",
            "probe": "stock_list",
            "market": args.market,
        }
        if isinstance(data, list):
            summary["count"] = len(data)
            summary["sample"] = data[:3]
        else:
            summary["raw_type"] = type(data).__name__
            summary["sample"] = data
        return summary

    data = run_tq_call(
        __file__,
        lambda tq: tq.get_market_snapshot(
            stock_code=args.stock_code,
            field_list=["Now", "LastClose", "Open"],
        ),
        preflight=False,
    )
    return {
        "status": "ok",
        "probe": "market_snapshot",
        "stock_code": args.stock_code,
        "sample": data,
    }

candidate_groups = describe_tdx_user_dir_candidates()
merged_candidates = _merge_candidates(candidate_groups)
selected_user_dir = find_tdx_user_dir()

report = {
    "platform": platform.system(),
    "config": load_config(),
}

report["selected_user_dir"] = str(selected_user_dir) if selected_user_dir else None
report["selected"] = _build_selected_summary(report["selected_user_dir"], merged_candidates)

if args.show_candidates:
    report["candidates"] = merged_candidates

module_info = {
    "load_status": "not_started",
    "module_file": None,
    "available_methods": {},
}
try:
    module = _load_external_module()
    module_info["load_status"] = "ok"
    module_info["module_file"] = getattr(module, "__file__", None)
    tq_obj = getattr(module, "tq", None)
    for method_name in [
        "get_stock_list",
        "get_market_snapshot",
        "get_market_data",
        "formula_get_all",
        "formula_get_info",
    ]:
        module_info["available_methods"][method_name] = bool(
            tq_obj is not None and hasattr(tq_obj, method_name)
        )
except Exception as exc:
    module_info["load_status"] = "error"
    module_info["error_type"] = type(exc).__name__
    module_info["error"] = str(exc)

report["module"] = module_info

if module_info["load_status"] == "ok":
    try:
        report["probe"] = _run_probe()
    except Exception as exc:
        report["probe"] = {
            "status": "error",
            "probe": args.probe,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
else:
    report["probe"] = {
        "status": "skipped",
        "reason": "module_load_failed",
    }

report["summary"] = {
    "path_status": "ok" if report["selected"] and report["selected"].get("is_valid_user_dir") else "error",
    "module_status": module_info["load_status"],
    "probe_status": report["probe"]["status"],
    "ready_for_general_interfaces": bool(
        report["selected"]
        and report["selected"].get("is_valid_user_dir")
        and module_info["load_status"] == "ok"
        and report["probe"]["status"] == "ok"
    ),
}

print_output(report, args.output)
