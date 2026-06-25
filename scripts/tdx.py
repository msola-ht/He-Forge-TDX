from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from lib.tdx_unified import invoke


if __name__ == "__main__":
    raise SystemExit(invoke(sys.argv[1:], program_label="python scripts/tdx.py"))
