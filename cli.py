"""CLI entry point for the Binance Futures Testnet trading bot."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Auto-load .env from the same directory as this script
load_dotenv(Path(__file__).parent / ".env")

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import validate_order_params

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

# ANSI color codes — gracefully disabled on terminals that don't support them
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_GREEN  = "\033[92m"
_RED    = "\033[91m"
_YELLOW = "\033[93m"
_CYAN   = "\033[96m"


def _supports_color() -> bool:
    """Return True if the terminal supports ANSI color codes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    """Wrap text in an ANSI color code if the terminal supports it."""
    return f"{code}{text}{_RESET}" if _supports_color() else text


def print_banner() -> None:
    """Print a compact header banner."""
    print(_c("─" * 50, _CYAN))
    print(_c("  Binance Futures Testnet — Trading Bot", _BOLD))
    print(_c("─" * 50, _CYAN))


def print_summary(symbol: str, side: str, order_type: str,
                  quantity: float, price: float | None) -> None:
    """Print a formatted order request summary."""
    side_color = _GREEN if side == "BUY" else _RED
    print(_c("\nOrder Request Summary", _BOLD))
    print(_c("─" * 30, _CYAN))
    print(f"  Symbol   : {_c(symbol, _BOLD)}")
    print(f"  Side     : {_c(side, side_color)}")
    print(f"  Type     : {order_type}")
    print(f"  Quantity : {quantity}")
    if price is not None:
        print(f"  Price    : {price}")
    print(_c("─" * 30, _CYAN))


def confirm_order() -> bool:
    """Prompt the user to confirm before placing the order."""
    try:
        answer = input(_c("\nProceed with order? [y/N]: ", _YELLOW)).strip().lower()
        return answer in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        return False


def format_order_response(response: dict) -> str:
    """Format a successful order response for display."""
    lines = [
        f"  orderId    : {_c(str(response.get('orderId')), _BOLD)}",
        f"  status     : {_c(str(response.get('status')), _GREEN)}",
        f"  executedQty: {response.get('executedQty')}",
    ]
    if response.get("avgPrice") is not None:
        lines.append(f"  avgPrice   : {response.get('avgPrice')}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place Market or Limit orders on Binance Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.002 --price 50000\n"
        ),
    )
    parser.add_argument("--symbol",   required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",     required=True,  help="BUY or SELL")
    parser.add_argument("--type",     dest="order_type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True,  type=float, help="Amount to trade (must be > 0)")
    parser.add_argument("--price",    required=False, type=float, default=None,
                        help="Limit price (required for LIMIT orders, must be > 0)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompt and place order immediately")
    return parser


def main(argv=None) -> int:
    setup_logging()
    print_banner()

    parser = build_parser()
    args = parser.parse_args(argv)

    # Validate inputs before touching the API
    try:
        validate_order_params(
            args.symbol,
            args.side,
            args.order_type,
            args.quantity,
            args.price,
        )
    except ValueError as exc:
        print(_c(f"\n  Validation error: {exc}", _RED))
        print(_c("  Fix the above and try again.\n", _YELLOW))
        return 1

    # Print order request summary
    print_summary(args.symbol, args.side, args.order_type, args.quantity, args.price)

    # Confirmation prompt (skip with --yes flag)
    if not args.yes and not confirm_order():
        print(_c("\nOrder cancelled.\n", _YELLOW))
        return 0

    # Load credentials from environment
    api_key = os.environ.get("BINANCE_API_KEY", "")
    api_secret = os.environ.get("BINANCE_API_SECRET", "")

    client = BinanceFuturesClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=TESTNET_BASE_URL,
    )

    print(_c("\nPlacing order...", _CYAN))

    try:
        response = place_order(
            client,
            args.symbol,
            args.side,
            args.order_type,
            args.quantity,
            args.price,
        )
    except Exception as exc:
        print(_c(f"\n  Order placement failed: {exc}\n", _RED))
        return 1

    print(_c("\nOrder placed successfully:", _GREEN))
    print(format_order_response(response))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
