"""Input validation for order parameters."""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
) -> None:
    """Validate order parameters before sending to the API.

    Raises:
        ValueError: with a descriptive message if any parameter is invalid.
    """
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    if quantity <= 0:
        raise ValueError(
            f"Invalid quantity '{quantity}'. Quantity must be a positive number."
        )

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        if price <= 0:
            raise ValueError(
                f"Invalid price '{price}'. Price must be a positive number for LIMIT orders."
            )
