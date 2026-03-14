"""
Tests for CLI output formatting.
"""
import sys
import pytest
from unittest.mock import patch
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Property 2: Order response output contains required fields
# Feature: trading-bot, Property 2: Order response output contains required fields
# Validates: Requirements 1.3
# ---------------------------------------------------------------------------

from cli import format_order_response

order_id_strategy = st.integers(min_value=1, max_value=10**15)
status_strategy = st.sampled_from(["NEW", "PARTIALLY_FILLED", "FILLED", "CANCELED"])
executed_qty_strategy = st.floats(min_value=0.0, max_value=1_000_000.0,
                                  allow_nan=False, allow_infinity=False)
avg_price_strategy = st.one_of(
    st.none(),
    st.floats(min_value=0.01, max_value=1_000_000.0, allow_nan=False, allow_infinity=False),
)


@given(
    order_id=order_id_strategy,
    status=status_strategy,
    executed_qty=executed_qty_strategy,
    avg_price=avg_price_strategy,
)
@settings(max_examples=100)
def test_order_response_output_contains_required_fields(order_id, status, executed_qty, avg_price):
    """
    # Feature: trading-bot, Property 2: Order response output contains required fields
    # Validates: Requirements 1.3

    For any successful order response dict containing orderId, status, executedQty,
    and optionally avgPrice, the formatted output string must contain each of those
    fields' values.
    """
    response = {
        "orderId": order_id,
        "status": status,
        "executedQty": executed_qty,
    }
    if avg_price is not None:
        response["avgPrice"] = avg_price

    output = format_order_response(response)

    assert str(order_id) in output, f"orderId {order_id!r} not found in output: {output!r}"
    assert status in output, f"status {status!r} not found in output: {output!r}"
    assert str(executed_qty) in output, f"executedQty {executed_qty!r} not found in output: {output!r}"
    if avg_price is not None:
        assert str(avg_price) in output, f"avgPrice {avg_price!r} not found in output: {output!r}"


# ---------------------------------------------------------------------------
# Unit tests for CLI output and error paths (task 5.2)
# Validates: Requirements 1.4, 1.5, 2.3
# ---------------------------------------------------------------------------

from cli import main


def test_success_output_contains_required_fields(capsys):
    """Success output must contain orderId, status, executedQty. Validates: Requirements 1.4"""
    mock_response = {
        "orderId": 123456,
        "status": "NEW",
        "executedQty": "0",
        "avgPrice": "0.00",
    }
    with patch("cli.place_order", return_value=mock_response), \
         patch("cli.BinanceFuturesClient"):
        rc = main(["--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--quantity", "0.01", "--yes"])

    captured = capsys.readouterr()
    assert rc == 0
    assert "123456" in captured.out
    assert "NEW" in captured.out
    assert "0" in captured.out


def test_failure_output_on_api_error(capsys):
    """Failure output must contain failure message and error details. Validates: Requirements 1.5"""
    with patch("cli.place_order", side_effect=Exception("API error: -1121")), \
         patch("cli.BinanceFuturesClient"):
        rc = main(["--symbol", "BTCUSDT", "--side", "BUY", "--type", "MARKET", "--quantity", "0.01", "--yes"])

    captured = capsys.readouterr()
    assert rc == 1
    assert "failed" in captured.out.lower()
    assert "API error: -1121" in captured.out


def test_limit_order_missing_price_prints_validation_error(capsys):
    """LIMIT order without --price must print a validation error. Validates: Requirements 2.3"""
    rc = main(["--symbol", "BTCUSDT", "--side", "BUY", "--type", "LIMIT", "--quantity", "0.01"])

    captured = capsys.readouterr()
    assert rc == 1
    assert "price" in captured.out.lower()
