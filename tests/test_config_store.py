from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch

from lib.pathing.config_store import load_config, save_config
from lib.pathing.discovery import iter_candidate_user_dir_specs


class ConfigStoreTests(unittest.TestCase):
    def test_config_file_can_be_overridden_by_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = f"{tmpdir}/tdx-config.json"

            with patch.dict("os.environ", {"TDX_CONFIG_FILE": config_file}, clear=False):
                save_config({"tdx_user_dir": "D:/new_tdx64/PYPlugins/user"})
                loaded = load_config()

        self.assertEqual(loaded["tdx_user_dir"], "D:/new_tdx64/PYPlugins/user")

    def test_candidate_specs_report_overridden_config_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = f"{tmpdir}/tdx-config.json"

            with patch.dict("os.environ", {"TDX_CONFIG_FILE": config_file}, clear=False):
                save_config({"tdx_user_dir": "D:/new_tdx64/PYPlugins/user"})
                specs = list(iter_candidate_user_dir_specs())

        config_spec = next(spec for spec in specs if spec["source"] == "config")
        self.assertEqual(config_spec["detail"], config_file)


if __name__ == "__main__":
    unittest.main()
