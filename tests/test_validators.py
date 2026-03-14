"""
Property-based tests for input validators.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from bot.validators import validate_order_params

VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]


# ---------------------------------------------------------------------------
# Property 3: Invalid side or order type values are rejected
# Feature: trading-bot, Property 3: Invalid side or order type values are rejected
# Validates: Requirements 2.1, 2.2
# ---------------------------------------------------------------------------

@given(
    symbol=st.just("BTCUSDT"),
    side=st.text(min_size=1).filter(lambda s: s not in VALID_SIDES),
    order_type=st.sampled_from(VALID_ORDER_TYPES),
    quantity=st.floats(min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_invalid_side_is_rejected(symbol, side, order_type, quantity):
    """
    # Feature: trading-bot, Property 3: Invalid side or order type values are rejected
    # Validates: Requirements 2.1

    For any string that is not in {BUY, SELL} when used as side,
    the validator must raise a ValueError with a non-empty message.
    """
    price = 100.0 if order_type == "LIMIT" else None
    with pytest.raises(ValueError) as exc_info:
        validate_order_params(symbol, side, order_type, quantity, price)
    assert str(exc_info.value), "ValueError message must be non-empty"


@given(
    symbol=st.just("BTCUSDT"),
    side=st.sampled_from(VALID_SIDES),
    order_type=st.text(min_size=1).filter(lambda s: s not in VALID_ORDER_TYPES),
    quantity=st.floats(min_value=0.001, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_invalid_order_type_is_rejected(symbol, side, order_type, quantity):
    """
    # Feature: trading-bot, Property 3: Invalid side or order type values are rejected
    # Validates: Requirements 2.2

    For any string that is not in {MARKET, LIMIT} when used as order type,
    the validator must raise a ValueError with a non-empty message.
    """
    with pytest.raises(ValueError) as exc_info:
        validate_order_params(symbol, side, order_type, quantity, None)
    assert str(exc_info.value), "ValueError message must be non-empty"


# ---------------------------------------------------------------------------
# Property 4: Non-positive quantity or price values are rejected
# Feature: trading-bot, Property 4: Non-positive quantity or price values are rejected
# Validates: Requirements 2.4, 2.5
# ---------------------------------------------------------------------------

@given(
    symbol=st.just("BTCUSDT"),
    side=st.sampled_from(VALID_SIDES),
    quantity=st.one_of(
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
        st.just(0.0),
    ),
)
@settings(max_examples=100)
def test_non_positive_quantity_is_rejected(symbol, side, quantity):
    """
    # Feature: trading-bot, Property 4: Non-positive quantity or price values are rejected
    # Validates: Requirements 2.4

    For any quantity <= 0, the validator must raise a ValueError.
    """
    with pytest.raises(ValueError):
        validate_order_params(symbol, side, "MARKET", quantity, None)


@given(
    symbol=st.just("BTCUSDT"),
    side=st.sampled_from(VALID_SIDES),
    price=st.one_of(
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
        st.just(0.0),
    ),
)
@settings(max_examples=100)
def test_non_positive_price_for_limit_is_rejected(symbol, side, price):
    """
    # Feature: trading-bot, Property 4: Non-positive quantity or price values are rejected
    # Validates: Requirements 2.5

    For any price <= 0 when order type is LIMIT, the validator must raise a ValueError.
    """
    with pytest.raises(ValueError):
        validate_order_params(symbol, side, "LIMIT", 1.0, price)
