from __future__ import annotations

import os
import platform
from pathlib import Path
import re

from .config_store import load_config, resolve_config_file

COMMON_TDX_ROOTS = (
    Path("C:/new_tdx64"),
    Path("C:/new_tdx"),
    Path("D:/new_tdx64"),
    Path("D:/new_tdx"),
    Path("E:/new_tdx64"),
    Path("E:/new_tdx"),
)

REGISTRY_KEY_PATHS = (
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\通达信金融终端64",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\通达信专业版",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\通达信金融终端(量化模拟)",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\通达信金融终端(测试)",
)
def is_mock_tdx_user_dir(user_dir: Path) -> bool:
    """保留兼容出口；当前不再根据路径名猜测客户端类型。"""
    return False


def _validate_user_dir(user_dir: Path) -> bool:
    return user_dir.is_dir() and (user_dir / "tqcenter.py").is_file()


def _user_dir_diagnostics(user_dir: Path) -> dict:
    plugin_dir = user_dir.parent
    install_root = plugin_dir.parent
    tqcenter_path = user_dir / "tqcenter.py"
    return {
        "candidate_user_dir": str(user_dir),
        "user_dir_exists": user_dir.is_dir(),
        "tqcenter_exists": tqcenter_path.is_file(),
        "plugin_dir_exists": plugin_dir.is_dir(),
        "tpythclient_exists": (plugin_dir / "TPythClient.dll").is_file(),
        "tpyth_exists": (plugin_dir / "TPyth.dll").is_file(),
        "tdxw_exists": (install_root / "TdxW.exe").is_file(),
        "install_root": str(install_root),
        "is_mock_like": is_mock_tdx_user_dir(user_dir),
        "is_valid_user_dir": _validate_user_dir(user_dir),
    }


def _iter_path_variants(user_dir: Path):
    raw = str(user_dir).strip()
    if not raw:
        return

    current_platform = platform.system()
    seen = set()

    def _yield(path_str: str):
        normalized = path_str.replace("\\", "/")
        if normalized in seen:
            return
        seen.add(normalized)
        yield Path(path_str)

    yield from _yield(raw)

    if current_platform == "Windows":
        return

    m_wsl = re.match(r"^/mnt/([a-zA-Z])/(.+)$", raw.replace("\\", "/"))
    if m_wsl:
        drive = m_wsl.group(1).upper()
        rest = m_wsl.group(2)
        yield from _yield(f"{drive}:/{rest}")

    m_win = re.match(r"^([a-zA-Z]):[\\/](.+)$", raw)
    if m_win:
        drive = m_win.group(1).lower()
        rest = m_win.group(2).replace("\\", "/")
        yield from _yield(f"/mnt/{drive}/{rest}")


def _iter_registry_user_dirs():
    if platform.system() != "Windows":
        return

    try:
        import winreg
    except ImportError:
        return

    for key_path in REGISTRY_KEY_PATHS:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                install_root, _ = winreg.QueryValueEx(key, "InstallLocation")
        except FileNotFoundError:
            continue

        yield Path(install_root) / "PYPlugins" / "user"


def _include_common_roots() -> bool:
    return platform.system() != "Windows"


def iter_candidate_user_dir_specs():
    configured = load_config().get("tdx_user_dir")
    if configured:
        yield {
            "source": "config",
            "detail": str(resolve_config_file()),
            "path": Path(configured),
        }

    env_user_dir = os.environ.get("TDX_USER_DIR")
    if env_user_dir:
        yield {
            "source": "env_tdx_user_dir",
            "detail": "TDX_USER_DIR",
            "path": Path(env_user_dir),
        }

    env_root = os.environ.get("TDX_ROOT")
    if env_root:
        yield {
            "source": "env_tdx_root",
            "detail": "TDX_ROOT",
            "path": Path(env_root) / "PYPlugins" / "user",
        }

    if platform.system() == "Windows":
        try:
            import winreg
        except ImportError:
            pass
        else:
            for key_path in REGISTRY_KEY_PATHS:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_root, _ = winreg.QueryValueEx(key, "InstallLocation")
                except FileNotFoundError:
                    continue

                yield {
                    "source": "registry",
                    "detail": key_path,
                    "path": Path(install_root) / "PYPlugins" / "user",
                }

    if _include_common_roots():
        for root in COMMON_TDX_ROOTS:
            yield {
                "source": "common_root",
                "detail": str(root),
                "path": root / "PYPlugins" / "user",
            }


def describe_tdx_user_dir_candidates() -> list[dict]:
    descriptions = []
    for spec in iter_candidate_user_dir_specs():
        variants = list(_iter_path_variants(spec["path"]))
        variant_rows = []
        for variant in variants:
            row = {
                "path": str(variant),
                **_user_dir_diagnostics(variant),
            }
            variant_rows.append(row)

        descriptions.append(
            {
                "source": spec["source"],
                "detail": spec["detail"],
                "raw_path": str(spec["path"]),
                "variants": variant_rows,
            }
        )

    return descriptions


def iter_candidate_user_dirs():
    configured = load_config().get("tdx_user_dir")
    if configured:
        yield Path(configured)

    env_user_dir = os.environ.get("TDX_USER_DIR")
    if env_user_dir:
        yield Path(env_user_dir)

    env_root = os.environ.get("TDX_ROOT")
    if env_root:
        yield Path(env_root) / "PYPlugins" / "user"

    for user_dir in _iter_registry_user_dirs() or ():
        yield user_dir

    if _include_common_roots():
        for root in COMMON_TDX_ROOTS:
            yield root / "PYPlugins" / "user"


def find_tdx_user_dir() -> Path | None:
    seen = set()
    for spec in iter_candidate_user_dir_specs():
        variants = list(_iter_path_variants(spec["path"]))
        for candidate in variants:
            normalized = str(candidate)
            if normalized in seen:
                continue
            seen.add(normalized)

            if not _validate_user_dir(candidate):
                continue

            return candidate

    return None
