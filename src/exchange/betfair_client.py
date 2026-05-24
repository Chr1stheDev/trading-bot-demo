"""
exchange/betfair_client.py
--------------------------
Betfair Exchange execution via betfairlightweight.
Supports Back, Lay, and Each-Way betting.

Each-way = two separate bets: Win market + Place market.
"""

import uuid
import betfairlightweight
from betfairlightweight.filters import market_filter, price_projection
from src.exchange.base import BaseExchange, FillResult
from src.parser import RacingOrder


class BetfairClient(BaseExchange):

    def __init__(self, username: str, password: str, app_key: str,
                 cert_path: str, key_path: str):
        self._client = betfairlightweight.APIClient(
            username=username,
            password=password,
            app_key=app_key,
            certs=(cert_path, key_path),
        )
        self._connected = False

    async def connect(self) -> None:
        self._client.login()
        self._connected = True
        print("[Betfair] Logged in")

    async def disconnect(self) -> None:
        self._client.logout()
        self._connected = False
        print("[Betfair] Logged out")

    async def is_connected(self) -> bool:
        return self._connected

    async def place_order(self, order) -> FillResult:
        if not isinstance(order, RacingOrder):
            return FillResult(
                success=False, order_id="", fill_price=None, quantity=0,
                message="Betfair client only supports RacingOrder"
            )

        try:
            if order.action == "EACHWAY":
                return await self._place_each_way(order)
            else:
                return await self._place_single(order)

        except Exception as e:
            return FillResult(
                success=False, order_id="", fill_price=None, quantity=0,
                message=f"Betfair error: {str(e)}"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _place_single(self, order: RacingOrder) -> FillResult:
        side = "BACK" if order.action == "BACK" else "LAY"
        market_id, selection_id = self._resolve_selection(order.selection)

        instructions = [{
            "selectionId": selection_id,
            "side": side,
            "orderType": "LIMIT",
            "limitOrder": {
                "size": order.stake,
                "price": order.odds,
                "persistenceType": "LAPSE",
            },
        }]

        response = self._client.betting.place_orders(
            market_id=market_id,
            instructions=instructions,
        )

        if response.status == "SUCCESS":
            result = response.instruction_reports[0]
            order_id = result.bet_id or str(uuid.uuid4())[:8]
            fill_price = result.average_price_matched or order.odds
            return FillResult(
                success=True,
                order_id=order_id,
                fill_price=fill_price,
                quantity=1,
                message=(
                    f"{order.action} {order.selection} @ {fill_price} "
                    f"stake £{order.stake} | ID: {order_id}"
                ),
            )
        else:
            return FillResult(
                success=False, order_id="", fill_price=None, quantity=0,
                message=f"Betfair rejected order: {response.error_code}"
            )

    async def _place_each_way(self, order: RacingOrder) -> FillResult:
        """Each-way = Win bet + Place bet placed separately."""
        win_order = RacingOrder(
            action="BACK",
            selection=order.selection,
            odds=order.odds,
            stake=order.stake,
        )
        place_order = RacingOrder(
            action="BACK",
            selection=order.selection,
            odds=round((order.odds - 1) / 4 + 1, 2),  # standard 1/4 odds
            stake=order.stake,
        )

        win_result = await self._place_single(win_order)
        place_result = await self._place_single(place_order)

        success = win_result.success and place_result.success
        return FillResult(
            success=success,
            order_id=f"{win_result.order_id}/{place_result.order_id}",
            fill_price=win_result.fill_price,
            quantity=1,
            message=(
                f"Each-Way {order.selection} @ {order.odds} stake £{order.stake}\n"
                f"  WIN   → {win_result.message}\n"
                f"  PLACE → {place_result.message}"
            ),
        )

    def _resolve_selection(self, selection_name: str) -> tuple[str, int]:
        """
        Look up market_id and selection_id from Betfair API.
        In production this queries the live markets catalogue.
        Simplified here for demo clarity.
        """
        raise NotImplementedError(
            "Selection resolution requires live Betfair market catalogue query. "
            "Implemented in production via betfairlightweight list_market_catalogue."
        )
