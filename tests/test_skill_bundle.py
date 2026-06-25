from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "tdx-direct-use" / "scripts" / "refresh_bundle.py"


def _load_refresh_bundle_module():
    spec = importlib.util.spec_from_file_location("tdx_direct_use_refresh_bundle", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillBundleTests(unittest.TestCase):
    def test_refresh_bundle_copies_runtime_and_references_but_skips_private_files(self) -> None:
        module = _load_refresh_bundle_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            repo_root = tmp_path / "repo"
            skill_dir = tmp_path / "skill"
            bundle_dir = skill_dir / "bundle"

            (repo_root / "lib").mkdir(parents=True)
            (repo_root / "scripts").mkdir(parents=True)
            (skill_dir / "scripts").mkdir(parents=True)

            (repo_root / "tdx.py").write_text("print('root')\n", encoding="utf-8")
            (repo_root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (repo_root / "requirements.txt").write_text("pandas>=2.0\n", encoding="utf-8")
            (repo_root / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
            (repo_root / "README.md").write_text("# readme\n", encoding="utf-8")
            (repo_root / "scripts" / "README.md").write_text("# scripts\n", encoding="utf-8")
            (repo_root / "lib" / "__init__.py").write_text("", encoding="utf-8")
            (repo_root / "lib" / "tdx_config.json").write_text('{"secret":1}\n', encoding="utf-8")
            (repo_root / "lib" / "tdx_subscribe_state.json").write_text('["000001.SZ"]\n', encoding="utf-8")
            (repo_root / "lib" / "runtime.py").write_text("print('runtime')\n", encoding="utf-8")
            (repo_root / "lib" / "runtime.pyc").write_bytes(b"pyc")
            (repo_root / "scripts" / "__init__.py").write_text("", encoding="utf-8")
            (repo_root / "scripts" / "get_market_snapshot.py").write_text("print('snapshot')\n", encoding="utf-8")

            module.REPO_ROOT = repo_root
            module.SKILL_DIR = skill_dir
            module.BUNDLE_DIR = bundle_dir

            result = module.main()

            self.assertEqual(result, 0)
            self.assertTrue((bundle_dir / "tdx.py").is_file())
            self.assertTrue((bundle_dir / "lib" / "runtime.py").is_file())
            self.assertTrue((bundle_dir / "scripts" / "get_market_snapshot.py").is_file())
            self.assertTrue((bundle_dir / "references" / "AGENTS.md").is_file())
            self.assertTrue((bundle_dir / "references" / "README.md").is_file())
            self.assertTrue((bundle_dir / "references" / "scripts-README.md").is_file())
            self.assertFalse((bundle_dir / "lib" / "tdx_config.json").exists())
            self.assertFalse((bundle_dir / "lib" / "tdx_subscribe_state.json").exists())
            self.assertFalse((bundle_dir / "lib" / "runtime.pyc").exists())

    def test_run_tdx_wrapper_uses_its_own_bundle_path_instead_of_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            skill_dir = tmp_path / "tdx-direct-use"
            bundle_dir = skill_dir / "bundle"
            other_cwd = tmp_path / "other"

            bundle_dir.mkdir(parents=True)
            other_cwd.mkdir()

            (skill_dir / "run_tdx.py").write_text(
                (ROOT / "skills" / "tdx-direct-use" / "run_tdx.py").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (bundle_dir / "tdx.py").write_text(
                "import json, sys\n"
                "print(json.dumps({'argv': sys.argv[1:]}))\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(skill_dir / "run_tdx.py"),
                    "get-divid-factors",
                    "--stock_code",
                    "000001.SZ",
                ],
                cwd=other_cwd,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("get-divid-factors", result.stdout)
            self.assertIn("000001.SZ", result.stdout)


if __name__ == "__main__":
    unittest.main()
