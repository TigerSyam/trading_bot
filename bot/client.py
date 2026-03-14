"""Binance Futures Testnet REST API client."""

import hashlib
import hmac
import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

RECV_WINDOW = 5000


class BinanceFuturesClient:
    """Wraps HTTP communication with the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, base_url: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def _build_params(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        """Assemble unsigned order parameters."""
        params: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "recvWindow": RECV_WINDOW,
            "timestamp": int(time.time() * 1000),
        }
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"
        return params

    def _sign(self, params: dict) -> str:
        """Return HMAC-SHA256 signature for the given params."""
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> dict:
        """Place an order on the Binance Futures Testnet.

        Returns:
            dict: The parsed JSON response from the API.

        Raises:
            requests.HTTPError: On non-2xx HTTP status.
            requests.RequestException: On network failure.
        """
        endpoint = f"{self.base_url}/fapi/v1/order"
        params = self._build_params(symbol, side, order_type, quantity, price)

        logger.info("Placing order — endpoint: %s, params: %s", endpoint, params)

        params["signature"] = self._sign(params)
        headers = {"X-MBX-APIKEY": self.api_key}

        try:
            response = requests.post(endpoint, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("Order response: %s", data)
            return data
        except requests.HTTPError as exc:
            logger.error("HTTP error placing order: %s", exc, exc_info=True)
            raise
        except requests.RequestException as exc:
            logger.error("Network error placing order: %s", exc, exc_info=True)
            raise
