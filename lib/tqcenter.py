from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from .config import find_tdx_user_dir

_MODULE_CACHE: ModuleType | None = None


def resolve_tdx_user_dir() -> Path:
    user_dir = find_tdx_user_dir()
    if user_dir is None:
        raise FileNotFoundError(
            "未找到可用的通达信 tqcenter.py。请先设置环境变量 TDX_USER_DIR / TDX_ROOT，"
            "或运行 scripts/setup_tdx_path.py 保存可用客户端的 PYPlugins/user 目录。"
        )
    return user_dir


def _load_external_module() -> ModuleType:
    global _MODULE_CACHE
    if _MODULE_CACHE is not None:
        return _MODULE_CACHE

    user_dir = resolve_tdx_user_dir()
    tqcenter_path = user_dir / "tqcenter.py"
    spec = importlib.util.spec_from_file_location(
        "_tdx_quant_external_tqcenter",
        tqcenter_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载 {tqcenter_path}")

    user_dir_str = str(user_dir)
    if user_dir_str not in sys.path:
        sys.path.insert(0, user_dir_str)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODULE_CACHE = module
    return module


class _ExportProxy:
    def __init__(self, export_name: str) -> None:
        self.export_name = export_name

    def _resolve(self):
        return getattr(_load_external_module(), self.export_name)

    def __getattr__(self, name: str):
        return getattr(self._resolve(), name)

    def __call__(self, *args, **kwargs):
        return self._resolve()(*args, **kwargs)


tq = _ExportProxy("tq")
tqconst = _ExportProxy("tqconst")
