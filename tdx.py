from __future__ import annotations

import sys

from lib.tdx_unified import invoke


if __name__ == "__main__":
    raise SystemExit(invoke(sys.argv[1:], program_label="python tdx.py"))
