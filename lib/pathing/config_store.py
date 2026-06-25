from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_CONFIG_FILE = Path(__file__).resolve().parents[1] / "tdx_config.json"
CONFIG_FILE_ENV_VAR = "TDX_CONFIG_FILE"
CONFIG_FILE = DEFAULT_CONFIG_FILE


def resolve_config_file() -> Path:
    configured = os.environ.get(CONFIG_FILE_ENV_VAR, "").strip()
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_CONFIG_FILE


def load_config() -> dict:
    config_file = resolve_config_file()
    if not config_file.exists():
        return {}

    try:
        return json.loads(config_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(config: dict) -> None:
    config_file = resolve_config_file()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def set_tdx_user_dir(user_dir: str) -> None:
    config = load_config()
    config["tdx_user_dir"] = str(Path(user_dir))
    save_config(config)
