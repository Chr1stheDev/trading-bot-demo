"""
parser.py
---------
Parses plain-text trade commands into structured dicts.

Supports two modes:
  - Options  : "Buy 2 SPY 660 Put 2026-06-05"
  - Racing   : "Back HORSE_NAME 2.5 10" / "EachWay HORSE_NAME 4.0 10"
"""

import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Literal


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class OptionsOrder:
    mode: Literal["options"] = field(default="options", init=False)
    action: str        # BUY | SELL
    quantity: int
    ticker: str
    strike: float
    right: str         # CALL | PUT
    expiry: str        # YYYY-MM-DD
    order_type: str = "MKT"

    def __str__(self):
        return (
            f"{self.action} {self.quantity}x {self.ticker} "
            f"{self.strike} {self.right} exp {self.expiry} [{self.order_type}]"
        )


@dataclass
class RacingOrder:
    mode: Literal["racing"] = field(default="racing", init=False)
    action: str        # BACK | LAY | EACHWAY
    selection: str
    odds: float
    stake: float

    def __str__(self):
        return f"{self.action} {self.selection} @ {self.odds} stake £{self.stake}"


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

OPTIONS_PATTERN = re.compile(
    r"(?P<action>buy|sell)\s+"
    r"(?P<qty>\d+)\s+"
    r"(?P<ticker>[A-Z]{1,5})\s+"
    r"(?P<strike>\d+(?:\.\d+)?)\s+"
    r"(?P<right>call|put)"
    r"(?:\s+(?P<expiry>\d{4}-\d{2}-\d{2}))?",
    re.IGNORECASE,
)

RACING_PATTERN = re.compile(
    r"(?P<action>back|lay|eachway)\s+"
    r"(?P<selection>.+?)\s+"
    r"(?P<odds>\d+(?:\.\d+)?)\s+"
    r"(?P<stake>\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Detects command type and returns a structured order object.
    Raises ValueError for unrecognised or malformed commands.
    """

    def parse(self, text: str) -> OptionsOrder | RacingOrder:
        text = text.strip()
        if not text:
            raise ValueError("Empty command")

        if self._looks_like_options(text):
            return self._parse_options(text)
        elif self._looks_like_racing(text):
            return self._parse_racing(text)
        else:
            raise ValueError(f"Unrecognised command format: '{text}'")

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    def _looks_like_options(self, text: str) -> bool:
        first = text.split()[0].lower()
        return first in ("buy", "sell")

    def _parse_options(self, text: str) -> OptionsOrder:
        m = OPTIONS_PATTERN.match(text)
        if not m:
            raise ValueError(
                f"Could not parse options command: '{text}'\n"
                "Expected: Buy <qty> <TICKER> <strike> <Call|Put> [YYYY-MM-DD]"
            )

        expiry = m.group("expiry")
        if expiry:
            # Validate date
            try:
                datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid expiry date: {expiry}")

        return OptionsOrder(
            action=m.group("action").upper(),
            quantity=int(m.group("qty")),
            ticker=m.group("ticker").upper(),
            strike=float(m.group("strike")),
            right=m.group("right").upper(),
            expiry=expiry or "",
        )

    # ------------------------------------------------------------------
    # Racing
    # ------------------------------------------------------------------

    def _looks_like_racing(self, text: str) -> bool:
        first = text.split()[0].lower()
        return first in ("back", "lay", "eachway")

    def _parse_racing(self, text: str) -> RacingOrder:
        m = RACING_PATTERN.match(text)
        if not m:
            raise ValueError(
                f"Could not parse racing command: '{text}'\n"
                "Expected: Back|Lay|EachWay <selection> <odds> <stake>"
            )

        odds = float(m.group("odds"))
        stake = float(m.group("stake"))

        if odds < 1.01:
            raise ValueError(f"Invalid odds: {odds} (minimum 1.01)")
        if stake <= 0:
            raise ValueError(f"Invalid stake: {stake}")

        return RacingOrder(
            action=m.group("action").upper(),
            selection=m.group("selection").strip(),
            odds=odds,
            stake=stake,
        )
