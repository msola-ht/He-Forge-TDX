from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from lib.cli.runtime import (
    SUBSCRIBE_STATE_FILE,
    add_output_argument,
    forget_subscriptions,
    initialize_tq,
    load_subscribe_state,
    parse_bool,
    print_json,
    print_output,
    remember_subscriptions,
    run_tq_call,
    save_subscribe_state,
    send_user_block_compat,
    tq_session,
)
