"""
tests/test_parser.py
--------------------
Unit tests for the dual-mode parser.
"""

import pytest
from src.parser import Parser, OptionsOrder, RacingOrder


@pytest.fixture
def parser():
    return Parser()


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

class TestOptionsParser:

    def test_buy_put_with_expiry(self, parser):
        order = parser.parse("Buy 2 SPY 660 Put 2026-06-05")
        assert isinstance(order, OptionsOrder)
        assert order.action == "BUY"
        assert order.quantity == 2
        assert order.ticker == "SPY"
        assert order.strike == 660.0
        assert order.right == "PUT"
        assert order.expiry == "2026-06-05"

    def test_sell_call_with_expiry(self, parser):
        order = parser.parse("Sell 1 AAPL 200 Call 2026-07-18")
        assert order.action == "SELL"
        assert order.ticker == "AAPL"
        assert order.right == "CALL"

    def test_sell_without_expiry(self, parser):
        order = parser.parse("Sell 1 SPY 660 Put")
        assert isinstance(order, OptionsOrder)
        assert order.expiry == ""

    def test_case_insensitive(self, parser):
        order = parser.parse("buy 5 spy 500 call 2026-09-19")
        assert order.action == "BUY"
        assert order.ticker == "SPY"
        assert order.right == "CALL"

    def test_invalid_options_command(self, parser):
        with pytest.raises(ValueError):
            parser.parse("Buy SPY")  # missing fields

    def test_invalid_expiry_date(self, parser):
        with pytest.raises(ValueError):
            parser.parse("Buy 1 SPY 660 Put 2026-13-01")  # month 13


# ---------------------------------------------------------------------------
# Racing
# ---------------------------------------------------------------------------

class TestRacingParser:

    def test_back_bet(self, parser):
        order = parser.parse("Back Thunderstruck 3.5 10")
        assert isinstance(order, RacingOrder)
        assert order.action == "BACK"
        assert order.selection == "Thunderstruck"
        assert order.odds == 3.5
        assert order.stake == 10.0

    def test_lay_bet(self, parser):
        order = parser.parse("Lay Silver Arrow 2.0 5")
        assert order.action == "LAY"
        assert order.selection == "Silver Arrow"

    def test_each_way(self, parser):
        order = parser.parse("EachWay Desert King 4.0 10")
        assert order.action == "EACHWAY"
        assert order.stake == 10.0

    def test_invalid_odds(self, parser):
        with pytest.raises(ValueError):
            parser.parse("Back Thunderstruck 0.5 10")  # odds < 1.01

    def test_invalid_stake(self, parser):
        with pytest.raises(ValueError):
            parser.parse("Back Thunderstruck 3.5 0")


# ---------------------------------------------------------------------------
# Unknown
# ---------------------------------------------------------------------------

class TestUnknownCommand:

    def test_gibberish(self, parser):
        with pytest.raises(ValueError):
            parser.parse("hello world")

    def test_empty_string(self, parser):
        with pytest.raises(ValueError):
            parser.parse("")
