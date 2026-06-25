from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from lib.formula.helpers import (
    DIVIDEND_TYPE_CHOICES,
    DIVIDEND_TYPE_HELP_TEXT,
    DIVIDEND_TYPE_INT_CHOICES,
    DIVIDEND_TYPE_INT_HELP_TEXT,
    FORMULA_REQUIRED_FIELDS,
    PERIOD_CHOICES,
    add_formula_preload_arguments,
    add_formula_prepare_arguments,
    call_tdx_formula_main,
    extract_formula_stock_data,
    load_json_file,
    maybe_formula_set_data_info,
    run_formula_preload,
)
