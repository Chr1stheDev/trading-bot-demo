# Trading Bot Demo

A modular Python bot that listens for plain-text trade commands via a messaging interface and executes them in real time through a financial exchange API.

Built across two live client projects:
- **Project 1** — Horse racing automation (Betfair Exchange API, each-way betting, live signals)
- **Project 2** — Options trading automation (Interactive Brokers, ib_insync, IB Gateway)

Both projects share the same core architecture. The exchange layer is swappable.

---

## Architecture

```
Messaging Interface (Listener)
        │
        ▼
   Message Parser
  (extracts structured trade data from plain text)
        │
        ▼
   Orchestrator
  (validates, gates on odds/price, routes to exchange)
        │
        ▼
  Exchange Client  ◄──── Abstract base (pluggable)
  ┌─────────────┐
  │  Betfair    │  ← Project 1 (racing)
  │  IBKR       │  ← Project 2 (options)
  │  Mock       │  ← testing / demo
  └─────────────┘
        │
        ▼
   Verifier
  (confirms fill, sends result back to user)
```

---

## Supported Command Formats

### Options (IBKR)
```
Buy 2 SPY 660 Put 2026-06-05
Sell 1 SPY 660 Put
Buy 5 AAPL 200 Call 2026-07-18
```

### Racing (Betfair)
```
Back HORSE_NAME 2.5 10
Lay HORSE_NAME 3.0 5
EachWay HORSE_NAME 4.0 10
```

---

## Project Structure

```
trading-bot-demo/
├── src/
│   ├── listener.py          # Messaging interface listener (async)
│   ├── parser.py            # Dual-mode parser: options + racing
│   ├── orchestrator.py      # Central coordinator & gate logic
│   ├── verifier.py          # Fill confirmation & reply
│   └── exchange/
│       ├── base.py          # Abstract exchange interface
│       ├── mock_exchange.py # Demo/paper mode (no live connection)
│       ├── betfair_client.py# Betfair Exchange (Project 1)
│       └── ibkr_client.py   # Interactive Brokers via ib_insync (Project 2)
├── tests/
│   ├── test_parser.py
│   └── test_mock_exchange.py
├── config.py
├── .env.example
└── requirements.txt
```

---

## Quickstart (Demo Mode)

```bash
git clone https://github.com/Chr1stheDev/trading-bot-demo
cd trading-bot-demo
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API credentials
python src/orchestrator.py --exchange mock
```

### Run Tests
```bash
pytest tests/ -v
```

---

## Exchange Setup

### Mock (no credentials needed)
```env
EXCHANGE=mock
```

### IBKR Paper Trading
```env
EXCHANGE=ibkr
IBKR_HOST=127.0.0.1
IBKR_PORT=7497        # 7497 = paper, 7496 = live
IBKR_CLIENT_ID=1
```
> IB Gateway must be running locally. Paper account only during development.

### Betfair
```env
EXCHANGE=betfair
BETFAIR_USERNAME=your_username
BETFAIR_PASSWORD=your_password
BETFAIR_APP_KEY=your_app_key
BETFAIR_CERT_PATH=./certs/betfair.crt
BETFAIR_KEY_PATH=./certs/betfair.key
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Abstract base exchange class | Swap exchanges without touching orchestrator logic |
| Parser returns structured dict | Decoupled from execution — easy to unit test |
| Confirmation step before order | User sees parsed intent and confirms before execution |
| Paper trading enforced in config | Live credentials never required during development |
| asyncio throughout | Non-blocking — listener and exchange calls run concurrently |

---

## Safety

- All development done on paper/demo accounts
- Live credentials never committed to repo (`.env` is gitignored)
- Orders require explicit confirmation reply before placement
- Each-way bets split into two separate orders with independent verification

---

## Tech Stack

- Python 3.12
- Telethon (messaging interface)
- ib_insync (IBKR / IB Gateway)
- betfairlightweight (Betfair Exchange)
- asyncio
- pytest

---

*This is a sanitized demo. Proprietary client logic, credentials, and market-specific configurations are excluded.*
