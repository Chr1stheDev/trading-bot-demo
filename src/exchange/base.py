"""
exchange/base.py
----------------
Abstract interface that all exchange clients must implement.
Swap exchanges without changing orchestrator logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class FillResult:
    success: bool
    order_id: str
    fill_price: Optional[float]
    quantity: int
    message: str


class BaseExchange(ABC):

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to exchange."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up connection."""
        ...

    @abstractmethod
    async def place_order(self, order) -> FillResult:
        """Place an order and return fill result."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Return True if exchange connection is live."""
        ...
