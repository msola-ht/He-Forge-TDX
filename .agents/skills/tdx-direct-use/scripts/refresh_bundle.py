from __future__ import annotations

import shutil
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
BUNDLE_DIR = SKILL_DIR / "bundle"

FILE_NAMES = (
    "tdx.py",
    "pyproject.toml",
    "requirements.txt",
)

DIR_NAMES = (
    "lib",
    "scripts",
)

REFERENCE_FILES = (
    ("AGENTS.md", "references/AGENTS.md"),
    ("README.md", "references/README.md"),
    ("scripts/README.md", "references/scripts-README.md"),
)

EXCLUDED_NAMES = {
    "__pycache__",
    "tdx_config.json",
    "tdx_subscribe_state.json",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
}


def _ignore(directory: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        if name in EXCLUDED_NAMES:
            ignored.add(name)
            continue
        if Path(name).suffix in EXCLUDED_SUFFIXES:
            ignored.add(name)
    return ignored


def _copy_file(name: str) -> None:
    source = REPO_ROOT / name
    target = BUNDLE_DIR / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_tree(name: str) -> None:
    source = REPO_ROOT / name
    target = BUNDLE_DIR / name
    shutil.copytree(source, target, ignore=_ignore, dirs_exist_ok=True)


def _copy_reference(source_name: str, target_name: str) -> None:
    source = REPO_ROOT / source_name
    target = BUNDLE_DIR / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    for name in FILE_NAMES:
        _copy_file(name)

    for name in DIR_NAMES:
        _copy_tree(name)

    for source_name, target_name in REFERENCE_FILES:
        _copy_reference(source_name, target_name)

    print(f"Bundled snapshot refreshed at: {BUNDLE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
