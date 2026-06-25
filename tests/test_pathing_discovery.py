from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from lib.pathing.discovery import find_tdx_user_dir, is_mock_tdx_user_dir, iter_candidate_user_dir_specs


class PathingDiscoveryTests(unittest.TestCase):
    def test_is_mock_tdx_user_dir_no_longer_guesses_from_path_name(self) -> None:
        self.assertFalse(is_mock_tdx_user_dir(Path("D:/Tools/new_tdx_mock/PYPlugins/user")))
        self.assertFalse(is_mock_tdx_user_dir(Path("D:/通达信模拟/PYPlugins/user")))
        self.assertFalse(is_mock_tdx_user_dir(Path("C:/new_tdx64/PYPlugins/user")))

    def test_find_tdx_user_dir_returns_first_valid_candidate(self) -> None:
        first_path = Path("D:/Tools/new_tdx_mock/PYPlugins/user")
        second_path = Path("C:/new_tdx64/PYPlugins/user")

        with patch(
            "lib.pathing.discovery.iter_candidate_user_dir_specs",
            return_value=[
                {"source": "common_root", "detail": "first", "path": first_path},
                {"source": "common_root", "detail": "second", "path": second_path},
            ],
        ):
            with patch("lib.pathing.discovery._validate_user_dir", return_value=True):
                selected = find_tdx_user_dir()

        self.assertEqual(selected, first_path)

    def test_iter_candidate_user_dir_specs_skips_common_roots_on_windows(self) -> None:
        with patch("lib.pathing.discovery.platform.system", return_value="Windows"):
            with patch("lib.pathing.discovery.load_config", return_value={}):
                with patch.dict("lib.pathing.discovery.os.environ", {}, clear=True):
                    with patch("lib.pathing.discovery.REGISTRY_KEY_PATHS", ()):
                        specs = list(iter_candidate_user_dir_specs())

        self.assertEqual(specs, [])


if __name__ == "__main__":
    unittest.main()
