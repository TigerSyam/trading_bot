# Binance Futures Testnet Trading Bot

A Python CLI application for placing Market and Limit orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M perpetual futures).

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set API credentials

Obtain testnet API keys from [https://testnet.binancefuture.com](https://testnet.binancefuture.com).

**Option A — `.env` file (recommended)**

Create a `.env` file inside the `trading_bot/` directory:
```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```
The bot loads this automatically — no extra steps needed.

**Option B — environment variables**

```cmd
set BINANCE_API_KEY=your_testnet_api_key
set BINANCE_API_SECRET=your_testnet_api_secret
```

---

## CLI Usage

Run the bot from inside the `trading_bot/` directory:

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT> --quantity <QTY> [--price <PRICE>]
```

### Place a MARKET order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

### Place a LIMIT order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 50000
```

### Example success output

```
──────────────────────────────────────────────────
  Binance Futures Testnet — Trading Bot
──────────────────────────────────────────────────

Order Request Summary
──────────────────────────────
  Symbol   : BTCUSDT
  Side     : BUY
  Type     : MARKET
  Quantity : 0.002
──────────────────────────────

Proceed with order? [y/N]: y

Placing order...

Order placed successfully:
  orderId    : 12806816455
  status     : NEW
  executedQty: 0.000
  avgPrice   : 0.00
```

### Skip confirmation prompt

Use `--yes` (or `-y`) to place the order without being prompted:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --yes
```

### Example validation error output

```
  Validation error: Price is required for LIMIT orders.
  Fix the above and try again.
```

### Full parameter reference

```
python cli.py --help

  --symbol    Trading pair, e.g. BTCUSDT
  --side      BUY or SELL
  --type      MARKET or LIMIT
  --quantity  Amount to trade (must be > 0)
  --price     Limit price (required for LIMIT orders, must be > 0)
  --yes, -y   Skip confirmation prompt and place order immediately
```

---

## Bonus — Enhanced CLI UX

The CLI includes an enhanced user experience on top of the core requirements:

- colored output — green for BUY/success, red for SELL/errors, yellow for warnings
- confirmation prompt before every order (`[y/N]`) to prevent accidental placement
- `--yes` / `-y` flag to bypass the prompt for scripting or automation
- formatted order summary with dividers for readability
- descriptive validation error messages with actionable hints
- usage examples shown in `--help`

---

## Running Tests

```bash
pytest tests/
```

---

## Logs

All API requests, responses, and errors are written to `logs/trading_bot.log` with timestamps, log levels, and module names.

---

## Assumptions

- The bot targets the **Binance Futures Testnet** only (`https://testnet.binancefuture.com`). It is not intended for use against the live Binance API.
- API credentials must be set via environment variables `BINANCE_API_KEY` and `BINANCE_API_SECRET`. A `.env` file in the `trading_bot/` directory is also supported (loaded automatically via `python-dotenv`).
- Only **BTCUSDT** and other USDT-M perpetual futures symbols available on the testnet are supported.
- For LIMIT orders, `timeInForce` is hardcoded to `GTC` (Good Till Cancelled).
- The minimum order notional on BTCUSDT futures is **$100**. At ~$80k BTC, a minimum quantity of `0.002` is required.
- Quantity and price precision must conform to the symbol's trading rules on the testnet; the bot does not auto-adjust precision.
- Python 3.10 or later is required (uses `float | None` union type syntax).
