"""
tests/test_mock_exchange.py
---------------------------
Integration tests for MockExchange.
Verifies order routing and fill result structure.
"""

import asyncio
import pytest
from src.exchange.mock_exchange import MockExchange
from src.parser import OptionsOrder, RacingOrder


@pytest.fixture
async def exchange():
    ex = MockExchange(latency_ms=0)
    await ex.connect()
    yield ex
    await ex.disconnect()


class TestMockExchangeOptions:

    @pytest.mark.asyncio
    async def test_buy_put(self, exchange):
        order = OptionsOrder(
            action="BUY", quantity=2, ticker="SPY",
            strike=660.0, right="PUT", expiry="2026-06-05"
        )
        result = await exchange.place_order(order)
        assert result.success is True
        assert result.order_id != ""
        assert result.fill_price is not None
        assert result.quantity == 2

    @pytest.mark.asyncio
    async def test_sell_call(self, exchange):
        order = OptionsOrder(
            action="SELL", quantity=1, ticker="AAPL",
            strike=200.0, right="CALL", expiry="2026-07-18"
        )
        result = await exchange.place_order(order)
        assert result.success is True


class TestMockExchangeRacing:

    @pytest.mark.asyncio
    async def test_back_bet(self, exchange):
        order = RacingOrder(action="BACK", selection="Thunderstruck", odds=3.5, stake=10.0)
        result = await exchange.place_order(order)
        assert result.success is True
        assert "BACK" in result.message

    @pytest.mark.asyncio
    async def test_each_way(self, exchange):
        order = RacingOrder(action="EACHWAY", selection="Desert King", odds=4.0, stake=10.0)
        result = await exchange.place_order(order)
        assert result.success is True
        assert "/" in result.order_id  # two order IDs joined


class TestMockExchangeNotConnected:

    @pytest.mark.asyncio
    async def test_place_order_when_disconnected(self):
        exchange = MockExchange()
        order = OptionsOrder(
            action="BUY", quantity=1, ticker="SPY",
            strike=500.0, right="CALL", expiry="2026-06-20"
        )
        result = await exchange.place_order(order)
        assert result.success is False
        assert "Not connected" in result.message
