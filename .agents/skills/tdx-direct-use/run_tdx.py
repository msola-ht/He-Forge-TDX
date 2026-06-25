from __future__ import annotations

import runpy
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent
BUNDLE_DIR = SKILL_DIR / "bundle"
ENTRY_FILE = BUNDLE_DIR / "tdx.py"


def main(argv: list[str] | None = None) -> int:
    if not ENTRY_FILE.is_file():
        print(
            "未找到 bundle/tdx.py。请先在仓库内运行 "
            "`python skills/tdx-direct-use/scripts/refresh_bundle.py` 生成可携带快照。",
            file=sys.stderr,
        )
        return 1

    original_argv = sys.argv[:]
    bundle_dir_str = str(BUNDLE_DIR)
    inserted = False
    if bundle_dir_str not in sys.path:
        sys.path.insert(0, bundle_dir_str)
        inserted = True

    sys.argv = [str(ENTRY_FILE), *(argv if argv is not None else sys.argv[1:])]
    try:
        runpy.run_path(str(ENTRY_FILE), run_name="__main__")
        return 0
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        if exc.code is None:
            return 0
        return 1
    finally:
        sys.argv = original_argv
        if inserted:
            try:
                sys.path.remove(bundle_dir_str)
            except ValueError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
