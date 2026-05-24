"""
main.py
-------
Entry point. Runs the bot with the exchange specified in .env (default: mock).

Usage:
  python main.py              # uses EXCHANGE from .env
  python main.py --exchange mock
  python main.py --exchange ibkr
"""

import asyncio
import argparse
import os
from dotenv import load_dotenv

load_dotenv()


def build_exchange(name: str):
    name = name.lower()
    if name == "mock":
        from src.exchange.mock_exchange import MockExchange
        return MockExchange()
    elif name == "ibkr":
        from src.exchange.ibkr_client import IBKRClient
        return IBKRClient(
            host=os.environ.get("IBKR_HOST", "127.0.0.1"),
            port=int(os.environ.get("IBKR_PORT", 7497)),
            client_id=int(os.environ.get("IBKR_CLIENT_ID", 1)),
        )
    elif name == "betfair":
        from src.exchange.betfair_client import BetfairClient
        return BetfairClient(
            username=os.environ["BETFAIR_USERNAME"],
            password=os.environ["BETFAIR_PASSWORD"],
            app_key=os.environ["BETFAIR_APP_KEY"],
            cert_path=os.environ["BETFAIR_CERT_PATH"],
            key_path=os.environ["BETFAIR_KEY_PATH"],
        )
    else:
        raise ValueError(f"Unknown exchange: {name}. Choose mock | ibkr | betfair")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", default=os.environ.get("EXCHANGE", "mock"))
    args = parser.parse_args()

    exchange = build_exchange(args.exchange)
    print(f"[Main] Starting with exchange: {args.exchange.upper()}")

    from src.orchestrator import Orchestrator
    from src.listener import Listener

    orchestrator = Orchestrator(exchange=exchange)
    listener = Listener(orchestrator=orchestrator)

    await listener.start()


if __name__ == "__main__":
    asyncio.run(main())
