from __future__ import annotations

import unittest

from lib.tq_constants import (
    DIVIDEND_TYPE_CHOICES,
    DIVIDEND_TYPE_INT_CHOICES,
    MARKET_TYPE_DEFINITIONS,
    ORDER_STATUS_DEFINITIONS,
    ORDER_TYPE_DEFINITIONS,
    PERIOD_CHOICES,
    PRICE_TYPE_DEFINITIONS,
    dividend_type_to_int,
)


class TqConstantsTests(unittest.TestCase):
    def test_period_choices_match_documented_values(self) -> None:
        self.assertEqual(
            PERIOD_CHOICES,
            ["1m", "5m", "15m", "30m", "1h", "1d", "1w", "1mon", "1q", "1y", "tick"],
        )

    def test_dividend_type_mappings_cover_string_and_int_forms(self) -> None:
        self.assertEqual(DIVIDEND_TYPE_CHOICES, ["none", "front", "back"])
        self.assertEqual(DIVIDEND_TYPE_INT_CHOICES, [0, 1, 2])
        self.assertEqual(dividend_type_to_int("none"), 0)
        self.assertEqual(dividend_type_to_int("front"), 1)
        self.assertEqual(dividend_type_to_int("BACK"), 2)

    def test_market_type_definitions_include_common_suffixes(self) -> None:
        mapping = {item["name"]: item["value"] for item in MARKET_TYPE_DEFINITIONS}

        self.assertEqual(mapping[".SZ"], 0)
        self.assertEqual(mapping[".SH"], 1)
        self.assertEqual(mapping[".BJ"], 2)
        self.assertEqual(mapping[".HK"], 31)
        self.assertEqual(mapping[".US"], 74)
        self.assertEqual(mapping[".INE"], 30)

    def test_trade_related_reference_enums_are_complete(self) -> None:
        order_mapping = {item["name"]: item["value"] for item in ORDER_TYPE_DEFINITIONS}
        price_mapping = {item["name"]: item["value"] for item in PRICE_TYPE_DEFINITIONS}
        status_mapping = {item["name"]: item["value"] for item in ORDER_STATUS_DEFINITIONS}

        self.assertEqual(order_mapping["CREDIT_FIN_BUY"], 69)
        self.assertEqual(order_mapping["OPTION_CLOSE_SHORT"], 204)
        self.assertEqual(price_mapping, {"PRICE_MY": 0, "PRICE_SJ": 1, "PRICE_ZTJ": 2, "PRICE_DTJ": 3})
        self.assertEqual(status_mapping["WTSTATUS_ALLCD"], 5)


if __name__ == "__main__":
    unittest.main()
