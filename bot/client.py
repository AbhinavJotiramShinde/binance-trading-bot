from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()


class BinanceAPIError(Exception):
    """Raised when Binance returns an API-level error."""


class BinanceRequestError(Exception):
    """Raised when the HTTP request fails before a valid Binance response."""


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
        timeout: int = 15,
        logger: logging.Logger | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv('BINANCE_API_KEY', '')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET', '')
        self.base_url = (base_url or os.getenv('BINANCE_BASE_URL', 'https://testnet.binancefuture.com')).rstrip('/')
        self.timeout = timeout
        self.logger = logger or logging.getLogger('trading_bot')

        if not self.api_key or not self.api_secret:
            raise ValueError('Missing BINANCE_API_KEY or BINANCE_API_SECRET in environment variables or arguments.')

        self.session = requests.Session()
        self.session.headers.update({'X-MBX-APIKEY': self.api_key})

    def _sign_params(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()
        return f'{query_string}&signature={signature}'

    def _request(self, method: str, path: str, signed: bool = False, **params: Any) -> Dict[str, Any]:
        url = f'{self.base_url}{path}'
        method = method.upper()

        try:
            payload = {k: v for k, v in params.items() if v is not None}
            if signed:
                payload.setdefault('timestamp', int(time.time() * 1000))
                payload.setdefault('recvWindow', 5000)
                query = self._sign_params(payload)
                final_url = f'{url}?{query}'
                self.logger.info('API request | method=%s url=%s params=%s', method, url, payload)
                response = self.session.request(method, final_url, timeout=self.timeout)
            else:
                self.logger.info('API request | method=%s url=%s params=%s', method, url, payload)
                response = self.session.request(method, url, params=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            self.logger.exception('Network error during Binance request: %s', exc)
            raise BinanceRequestError(f'Network error: {exc}') from exc

        content_type = response.headers.get('Content-Type', '')
        data: Dict[str, Any]
        if 'application/json' in content_type:
            data = response.json()
        else:
            data = {'raw': response.text}

        self.logger.info('API response | status_code=%s body=%s', response.status_code, data)

        if response.status_code >= 400:
            msg = data.get('msg', response.text)
            code = data.get('code', 'UNKNOWN') if isinstance(data, dict) else 'UNKNOWN'
            raise BinanceAPIError(f'Binance API error ({code}): {msg}')

        return data

    def ping(self) -> Dict[str, Any]:
        return self._request('GET', '/fapi/v1/ping')

    def get_exchange_info(self) -> Dict[str, Any]:
        return self._request('GET', '/fapi/v1/exchangeInfo')

    def create_order(self, **params: Any) -> Dict[str, Any]:
        return self._request('POST', '/fapi/v1/order', signed=True, **params)
