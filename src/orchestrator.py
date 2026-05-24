"""
orchestrator.py
---------------
Central coordinator.
Parses incoming text → validates → routes to exchange → returns result.

Flow:
  1. Parse command
  2. Show parsed intent to user (confirmation step)
  3. On confirm → place order
  4. Return fill result
"""

import asyncio
from src.parser import Parser, OptionsOrder, RacingOrder
from src.exchange.base import BaseExchange
from src.verifier import Verifier


class Orchestrator:

    def __init__(self, exchange: BaseExchange):
        self.exchange = exchange
        self.parser = Parser()
        self.verifier = Verifier()
        self._pending: dict[int, OptionsOrder | RacingOrder] = {}  # user_id → pending order

    async def handle(self, text: str, user_id: int = 0) -> str:
        text = text.strip()

        # Confirmation reply
        if text.lower() in ("yes", "confirm", "ok", "y"):
            return await self._execute_pending(user_id)

        if text.lower() in ("no", "cancel", "n"):
            self._pending.pop(user_id, None)
            return "Order cancelled."

        # New command
        try:
            order = self.parser.parse(text)
        except ValueError as e:
            return f"Could not parse command:\n{e}"

        # Store pending and ask for confirmation
        self._pending[user_id] = order
        return (
            f"Confirm order?\n\n"
            f"{order}\n\n"
            f"Reply YES to place or NO to cancel."
        )

    async def _execute_pending(self, user_id: int) -> str:
        order = self._pending.pop(user_id, None)
        if not order:
            return "No pending order. Send a trade command first."

        if not await self.exchange.is_connected():
            await self.exchange.connect()

        result = await self.exchange.place_order(order)
        return self.verifier.format(result)
