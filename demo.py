"""
demo.py
-------
Zero-setup CLI demo. No Telegram, no API keys, no exchange connection.
Type trade commands directly in the terminal and see the bot respond live.

Usage:
  python demo.py

Supports:
  Buy 2 SPY 660 Put 2026-06-05
  Sell 1 SPY 660 Put
  Back Thunderstruck 3.5 10
  EachWay Desert King 4.0 10
  yes / no  (to confirm or cancel)
  quit      (to exit)
"""

import asyncio
from src.orchestrator import Orchestrator
from src.exchange.mock_exchange import MockExchange


BANNER = """
╔══════════════════════════════════════════════╗
║         Trading Bot — CLI Demo Mode          ║
║  Mock exchange · No credentials required     ║
╠══════════════════════════════════════════════╣
║  Options examples:                           ║
║    Buy 2 SPY 660 Put 2026-06-05              ║
║    Sell 1 SPY 660 Put                        ║
║    Buy 5 AAPL 200 Call 2026-07-18            ║
║                                              ║
║  Racing examples:                            ║
║    Back Thunderstruck 3.5 10                 ║
║    Lay Silver Arrow 2.0 5                    ║
║    EachWay Desert King 4.0 10                ║
║                                              ║
║  Confirm orders: yes / no                    ║
║  Exit: quit                                  ║
╚══════════════════════════════════════════════╝
"""


async def run():
    exchange = MockExchange()
    await exchange.connect()
    orchestrator = Orchestrator(exchange=exchange)

    print(BANNER)

    while True:
        try:
            text = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Demo] Exiting.")
            break

        if not text:
            continue

        if text.lower() == "quit":
            print("[Demo] Goodbye.")
            break

        response = await orchestrator.handle(text, user_id=0)
        print(f"\nbot > {response}\n")

    await exchange.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
