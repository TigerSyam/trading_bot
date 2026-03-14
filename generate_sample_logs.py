"""
Script to generate sample log entries by placing a MARKET and a LIMIT order
against the Binance Futures Testnet.

Usage:
    export BINANCE_API_KEY=<your_testnet_key>
    export BINANCE_API_SECRET=<your_testnet_secret>
    cd trading_bot
    python generate_sample_logs.py

Both runs are appended to logs/trading_bot.log.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the same directory as this script
load_dotenv(Path(__file__).parent / ".env")

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.validators import validate_order_params

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

# Adjust these to valid testnet values for your account
SYMBOL = "BTCUSDT"
MARKET_QUANTITY = 0.002   # ~$160 at ~$80k BTC, above the $100 minimum notional
LIMIT_QUANTITY = 0.002
LIMIT_PRICE = 50000.0  # below market so it rests on the book; notional = $100


def run_order(client, symbol, side, order_type, quantity, price=None):
    print(f"\n--- Placing {order_type} {side} order ---")
    try:
        validate_order_params(symbol, side, order_type, quantity, price)
        response = place_order(client, symbol, side, order_type, quantity, price)
        print(f"Success: orderId={response.get('orderId')}, status={response.get('status')}")
        return response
    except Exception as exc:
        print(f"Failed: {exc}")
        return None


def main():
    setup_logging()

    api_key = os.environ.get("BINANCE_API_KEY", "")
    api_secret = os.environ.get("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        print("ERROR: BINANCE_API_KEY and BINANCE_API_SECRET must be set.")
        sys.exit(1)

    client = BinanceFuturesClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=TESTNET_BASE_URL,
    )

    # Run 1: MARKET order
    run_order(client, SYMBOL, "BUY", "MARKET", MARKET_QUANTITY)

    # Run 2: LIMIT order (resting, well below market)
    run_order(client, SYMBOL, "BUY", "LIMIT", LIMIT_QUANTITY, LIMIT_PRICE)

    print("\nDone. Check logs/trading_bot.log for the full log output.")


if __name__ == "__main__":
    main()
