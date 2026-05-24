"""
exchange/mock_exchange.py
-------------------------
Simulates order placement for demo and testing purposes.
No live connection required.
"""

import asyncio
import random
import uuid
from src.exchange.base import BaseExchange, FillResult
from src.parser import OptionsOrder, RacingOrder


class MockExchange(BaseExchange):

    def __init__(self, latency_ms: int = 200):
        self._connected = False
        self._latency = latency_ms / 1000

    async def connect(self) -> None:
        await asyncio.sleep(0.1)
        self._connected = True
        print("[MockExchange] Connected (paper mode)")

    async def disconnect(self) -> None:
        self._connected = False
        print("[MockExchange] Disconnected")

    async def is_connected(self) -> bool:
        return self._connected

    async def place_order(self, order) -> FillResult:
        if not self._connected:
            return FillResult(
                success=False,
                order_id="",
                fill_price=None,
                quantity=0,
                message="Not connected to exchange",
            )

        await asyncio.sleep(self._latency)  # simulate network round-trip

        order_id = str(uuid.uuid4())[:8].upper()

        if isinstance(order, OptionsOrder):
            fill_price = round(order.strike * random.uniform(0.01, 0.05), 2)
            return FillResult(
                success=True,
                order_id=order_id,
                fill_price=fill_price,
                quantity=order.quantity,
                message=(
                    f"[MOCK] {order.action} {order.quantity}x "
                    f"{order.ticker} {order.strike} {order.right} "
                    f"filled @ ${fill_price} | ID: {order_id}"
                ),
            )

        elif isinstance(order, RacingOrder):
            if order.action == "EACHWAY":
                win_id = str(uuid.uuid4())[:8].upper()
                place_id = str(uuid.uuid4())[:8].upper()
                return FillResult(
                    success=True,
                    order_id=f"{win_id}/{place_id}",
                    fill_price=order.odds,
                    quantity=1,
                    message=(
                        f"[MOCK] Each-Way {order.selection} @ {order.odds} "
                        f"stake £{order.stake} | WIN:{win_id} PLACE:{place_id}"
                    ),
                )
            else:
                return FillResult(
                    success=True,
                    order_id=order_id,
                    fill_price=order.odds,
                    quantity=1,
                    message=(
                        f"[MOCK] {order.action} {order.selection} "
                        f"@ {order.odds} stake £{order.stake} | ID: {order_id}"
                    ),
                )

        return FillResult(
            success=False,
            order_id="",
            fill_price=None,
            quantity=0,
            message=f"Unknown order type: {type(order)}",
        )
