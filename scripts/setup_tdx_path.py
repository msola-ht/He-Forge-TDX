import argparse
import platform
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from lib.config import describe_tdx_user_dir_candidates, load_config, set_tdx_user_dir
from lib.cli.runtime import add_output_argument, print_output

SOURCE_PRIORITY = {
    "registry": 0,
    "config": 1,
    "env_tdx_user_dir": 2,
    "env_tdx_root": 3,
    "common_root": 4,
}

def _build_candidate_choices(show_all: bool) -> list[dict]:
    current = load_config().get("tdx_user_dir")
    is_windows = platform.system() == "Windows"
    merged = {}

    def _path_key(path: str) -> str:
        normalized = path.replace("\\", "/")
        return normalized.lower() if is_windows else normalized

    for group in describe_tdx_user_dir_candidates():
        for variant in group["variants"]:
            if not show_all and not variant["is_valid_user_dir"]:
                continue
            key = _path_key(variant["path"])
            choice = merged.get(key)
            if choice is None:
                choice = {
                    "index": 0,
                    "path": variant["path"],
                    "is_current": variant["path"] == current,
                    "user_dir_exists": variant["user_dir_exists"],
                    "tqcenter_exists": variant["tqcenter_exists"],
                    "tpythclient_exists": variant["tpythclient_exists"],
                    "tdxw_exists": variant["tdxw_exists"],
                    "is_mock_like": variant["is_mock_like"],
                    "is_valid_user_dir": variant["is_valid_user_dir"],
                    "sources": [],
                    "details": [],
                    "source_priority": SOURCE_PRIORITY.get(group["source"], 99),
                    "is_recommended": False,
                }
                merged[key] = choice
            else:
                choice["is_current"] = choice["is_current"] or (variant["path"] == current)
                choice["user_dir_exists"] = choice["user_dir_exists"] or variant["user_dir_exists"]
                choice["tqcenter_exists"] = choice["tqcenter_exists"] or variant["tqcenter_exists"]
                choice["tpythclient_exists"] = choice["tpythclient_exists"] or variant["tpythclient_exists"]
                choice["tdxw_exists"] = choice["tdxw_exists"] or variant["tdxw_exists"]
                choice["is_mock_like"] = choice["is_mock_like"] or variant["is_mock_like"]
                choice["is_valid_user_dir"] = choice["is_valid_user_dir"] or variant["is_valid_user_dir"]
                choice["source_priority"] = min(
                    choice["source_priority"],
                    SOURCE_PRIORITY.get(group["source"], 99),
                )

            if group["source"] not in choice["sources"]:
                choice["sources"].append(group["source"])
            if group["detail"] not in choice["details"]:
                choice["details"].append(group["detail"])

    choices = sorted(
        merged.values(),
        key=lambda item: (
            not item["is_valid_user_dir"],
            item["source_priority"],
            not item["is_current"],
            item["path"].lower() if is_windows else item["path"],
        ),
    )

    for item in choices:
        if item["is_valid_user_dir"] and "registry" in item["sources"]:
            item["is_recommended"] = True
            break
    else:
        for item in choices:
            if item["is_valid_user_dir"] and item["is_current"]:
                item["is_recommended"] = True
                break
        else:
            for item in choices:
                if item["is_valid_user_dir"]:
                    item["is_recommended"] = True
                    break

    for index, item in enumerate(choices, start=1):
        item["index"] = index

    return choices


parser = argparse.ArgumentParser(description="查找并保存通达信 PYPlugins/user 目录路径")
parser.add_argument(
    "--user-dir",
    default="",
    help="例如: E:/new_tdx64/PYPlugins/user",
)
parser.add_argument(
    "--pick",
    type=int,
    default=0,
    help="从自动找到的候选路径中按序号选择并保存",
)
parser.add_argument(
    "--show-all",
    action="store_true",
    help="列出全部候选路径（默认只列出有效候选）",
)
add_output_argument(parser)

args = parser.parse_args()

candidates = _build_candidate_choices(args.show_all)
current_config = load_config().get("tdx_user_dir")

if args.user_dir:
    user_dir = Path(args.user_dir)
    if not (user_dir / "tqcenter.py").is_file():
        raise FileNotFoundError(f"目录下未找到 tqcenter.py: {user_dir}")

    set_tdx_user_dir(args.user_dir)
    result = {
        "status": "ok",
        "action": "save_user_dir",
        "tdx_user_dir": args.user_dir,
        "is_mock_like": False,
    }
    print_output(result, args.output)
    raise SystemExit(0)

if args.pick:
    if not candidates:
        raise ValueError("当前没有可选择的候选路径，请改用 --user-dir 手动指定")
    selected = next((item for item in candidates if item["index"] == args.pick), None)
    if selected is None:
        raise ValueError(f"无效序号: {args.pick}")
    if not selected["is_valid_user_dir"]:
        raise ValueError(f"序号 {args.pick} 对应路径无效，不能保存")

    set_tdx_user_dir(selected["path"])
    result = {
        "status": "ok",
        "action": "pick_candidate",
        "tdx_user_dir": selected["path"],
        "is_mock_like": False,
        "sources": selected["sources"],
        "details": selected["details"],
    }
    print_output(result, args.output)
    raise SystemExit(0)

result = {
    "status": "ok",
    "action": "list_candidates",
    "current_config": current_config,
    "candidates": candidates,
}

if args.output == "raw":
    print(f"当前已保存路径: {current_config or '(未设置)'}")
    if not candidates:
        print("未找到可用候选路径。可用 --user-dir 手动指定，例如:")
        print("python scripts/setup_tdx_path.py --user-dir E:/new_tdx64/PYPlugins/user")
    else:
        valid_candidates = [item for item in candidates if item["is_valid_user_dir"]]
        invalid_candidates = [item for item in candidates if not item["is_valid_user_dir"]]

        def _print_candidate(item: dict) -> None:
            current_mark = " [当前]" if item["is_current"] else ""
            recommended_mark = " [推荐]" if item["is_recommended"] else ""
            print(
                f"{item['index']}. {item['path']}{current_mark}{recommended_mark}\n"
                f"   sources={','.join(item['sources'])} detail={' | '.join(item['details'])}\n"
                f"   tqcenter={item['tqcenter_exists']} TPythClient={item['tpythclient_exists']} "
                f"TdxW={item['tdxw_exists']} valid={item['is_valid_user_dir']}"
            )

        if valid_candidates:
            print("有效候选路径:")
            for item in valid_candidates:
                _print_candidate(item)
        else:
            print("未找到有效候选路径。")

        if args.show_all and invalid_candidates:
            print("\n其他未命中目录（仅兜底猜测，不代表已安装）:")
            for item in invalid_candidates:
                _print_candidate(item)

        if not args.show_all and invalid_candidates:
            print("\n已自动隐藏未命中目录；如需排查全部猜测路径，可加 --show-all。")

        print("\n确认后可执行:")
        print("python scripts/setup_tdx_path.py --pick <序号>")
        print("或手动指定:")
        print("python scripts/setup_tdx_path.py --user-dir E:/new_tdx64/PYPlugins/user")
else:
    print_output(result, args.output)
