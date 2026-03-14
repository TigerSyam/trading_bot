"""
Property-based tests for BinanceFuturesClient payload assembly.
"""
from hypothesis import given, settings
from hypothesis import strategies as st

from bot.client import BinanceFuturesClient

VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]

# Reusable strategy for valid symbols (non-empty uppercase alphanumeric)
symbol_strategy = st.from_regex(r"[A-Z]{3,10}", fullmatch=True)

# Positive floats suitable for quantity / price
positive_float = st.floats(min_value=0.001, max_value=1_000_000.0, allow_nan=False, allow_infinity=False)


def _make_client() -> BinanceFuturesClient:
    return BinanceFuturesClient(
        api_key="test_key",
        api_secret="test_secret",
        base_url="https://testnet.binancefuture.com",
    )


# ---------------------------------------------------------------------------
# Property 1: Valid order params produce correct API payload
# Feature: trading-bot, Property 1: Valid order params produce correct API payload
# Validates: Requirements 1.1, 1.2
# ---------------------------------------------------------------------------

@given(
    symbol=symbol_strategy,
    side=st.sampled_from(VALID_SIDES),
    quantity=positive_float,
)
@settings(max_examples=100)
def test_market_order_payload(symbol, side, quantity):
    """
    # Feature: trading-bot, Property 1: Valid order params produce correct API payload
    # Validates: Requirements 1.1

    For any valid MARKET order params, _build_params must include the correct
    symbol, side, type, and quantity, and must NOT include a price field.
    """
    client = _make_client()
    params = client._build_params(symbol, side, "MARKET", quantity, price=None)

    assert params["symbol"] == symbol
    assert params["side"] == side
    assert params["type"] == "MARKET"
    assert params["quantity"] == quantity
    assert "price" not in params


@given(
    symbol=symbol_strategy,
    side=st.sampled_from(VALID_SIDES),
    quantity=positive_float,
    price=positive_float,
)
@settings(max_examples=100)
def test_limit_order_payload(symbol, side, quantity, price):
    """
    # Feature: trading-bot, Property 1: Valid order params produce correct API payload
    # Validates: Requirements 1.2

    For any valid LIMIT order params, _build_params must include the correct
    symbol, side, type, quantity, and price fields.
    """
    client = _make_client()
    params = client._build_params(symbol, side, "LIMIT", quantity, price=price)

    assert params["symbol"] == symbol
    assert params["side"] == side
    assert params["type"] == "LIMIT"
    assert params["quantity"] == quantity
    assert params["price"] == price
