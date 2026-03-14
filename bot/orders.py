"""Order placement orchestration layer."""

from typing import Optional

from bot.client import BinanceFuturesClient


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> dict:
    """Place an order via the provided API client.

    Delegates directly to client.place_order, acting as the thin
    orchestration layer between the CLI and the API client.

    Args:
        client: An initialised BinanceFuturesClient instance.
        symbol: Trading pair, e.g. BTCUSDT.
        side: BUY or SELL.
        order_type: MARKET or LIMIT.
        quantity: Amount to trade (must be > 0).
        price: Limit price (required for LIMIT orders, must be > 0).

    Returns:
        dict: The parsed JSON order response from the Binance API.

    Raises:
        requests.HTTPError: On non-2xx HTTP status from the API.
        requests.RequestException: On network failure.
    """
    return client.place_order(symbol, side, order_type, quantity, price)
