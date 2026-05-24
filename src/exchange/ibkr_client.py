"""
exchange/ibkr_client.py
-----------------------
Interactive Brokers execution via ib_insync.
Connects to IB Gateway (paper or live).

Paper:  host=127.0.0.1  port=7497
Live:   host=127.0.0.1  port=7496
"""

import asyncio
from ib_insync import IB, Option, MarketOrder, LimitOrder, util
from src.exchange.base import BaseExchange, FillResult
from src.parser import OptionsOrder


class IBKRClient(BaseExchange):

    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
        self.host = host
        self.port = port
        self.client_id = client_id
        self._ib = IB()

    async def connect(self) -> None:
        await self._ib.connectAsync(self.host, self.port, clientId=self.client_id)
        print(f"[IBKR] Connected to IB Gateway at {self.host}:{self.port}")

    async def disconnect(self) -> None:
        self._ib.disconnect()
        print("[IBKR] Disconnected")

    async def is_connected(self) -> bool:
        return self._ib.isConnected()

    async def place_order(self, order) -> FillResult:
        if not isinstance(order, OptionsOrder):
            return FillResult(
                success=False, order_id="", fill_price=None, quantity=0,
                message="IBKR client only supports OptionsOrder"
            )

        try:
            # Step 1: Build and qualify the contract
            contract = Option(
                symbol=order.ticker,
                lastTradeDateOrContractMonth=order.expiry.replace("-", ""),
                strike=order.strike,
                right=order.right[0],   # 'C' or 'P'
                exchange="SMART",
                currency="USD",
            )

            qualified = await self._ib.qualifyContractsAsync(contract)
            if not qualified:
                return FillResult(
                    success=False, order_id="", fill_price=None, quantity=0,
                    message=(
                        f"Contract not found: {order.ticker} "
                        f"{order.strike} {order.right} {order.expiry}"
                    ),
                )

            contract = qualified[0]

            # Step 2: Place order
            ib_order = MarketOrder(action=order.action, totalQuantity=order.quantity)
            trade = self._ib.placeOrder(contract, ib_order)

            # Step 3: Wait for fill (timeout 30s)
            timeout = 30
            elapsed = 0
            while not trade.isDone() and elapsed < timeout:
                await asyncio.sleep(1)
                elapsed += 1

            if trade.orderStatus.status == "Filled":
                fill_price = trade.orderStatus.avgFillPrice
                order_id = str(trade.order.orderId)
                return FillResult(
                    success=True,
                    order_id=order_id,
                    fill_price=fill_price,
                    quantity=order.quantity,
                    message=(
                        f"{order.action} {order.quantity}x {order.ticker} "
                        f"{order.strike} {order.right} "
                        f"filled @ ${fill_price:.2f} | ID: {order_id}"
                    ),
                )
            else:
                return FillResult(
                    success=False,
                    order_id=str(trade.order.orderId),
                    fill_price=None,
                    quantity=0,
                    message=f"Order not filled. Status: {trade.orderStatus.status}",
                )

        except Exception as e:
            return FillResult(
                success=False, order_id="", fill_price=None, quantity=0,
                message=f"IBKR error: {str(e)}"
            )
