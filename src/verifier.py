"""
verifier.py
-----------
Formats FillResult into a human-readable reply sent back to the user.
"""

from src.exchange.base import FillResult


class Verifier:

    def format(self, result: FillResult) -> str:
        if result.success:
            return (
                f"✅ Order filled\n"
                f"──────────────\n"
                f"{result.message}\n"
                f"Order ID: {result.order_id}"
            )
        else:
            return (
                f"❌ Order failed\n"
                f"──────────────\n"
                f"{result.message}"
            )
