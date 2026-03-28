from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from bot.client import BinanceAPIError, BinanceFuturesClient, BinanceRequestError
from bot.logging_config import setup_logging
from bot.orders import build_order_payload, place_order
from bot.validators import ValidationError


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Place MARKET or LIMIT orders on Binance Futures Testnet (USDT-M).'
    )
    parser.add_argument('--symbol', required=True, help='Trading symbol, e.g. BTCUSDT')
    parser.add_argument('--side', required=True, help='BUY or SELL')
    parser.add_argument('--order-type', required=True, dest='order_type', help='MARKET or LIMIT')
    parser.add_argument('--quantity', required=True, help='Order quantity, e.g. 0.001')
    parser.add_argument('--price', help='Price required for LIMIT orders')
    parser.add_argument(
        '--base-url',
        default=None,
        help='Optional override for Binance base URL. Defaults to BINANCE_BASE_URL or https://testnet.binancefuture.com',
    )
    return parser


def print_summary(payload: Dict[str, Any]) -> None:
    print('\n=== ORDER REQUEST SUMMARY ===')
    print(json.dumps(payload, indent=2))


def print_response(response: Dict[str, Any]) -> None:
    print('\n=== ORDER RESPONSE DETAILS ===')
    print(f"orderId      : {response.get('orderId', 'N/A')}")
    print(f"status       : {response.get('status', 'N/A')}")
    print(f"executedQty  : {response.get('executedQty', 'N/A')}")
    print(f"avgPrice     : {response.get('avgPrice', 'N/A')}")
    print('\nFull response:')
    print(json.dumps(response, indent=2))


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    logger = setup_logging()

    try:
        payload = build_order_payload(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        print_summary(payload)

        client = BinanceFuturesClient(base_url=args.base_url, logger=logger)
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        print_response(response)
        print('\nSUCCESS: order placed successfully.')
        return 0

    except ValidationError as exc:
        logger.error('Validation failed: %s', exc)
        print(f'FAILURE: invalid input -> {exc}')
        return 2
    except BinanceAPIError as exc:
        logger.error('Binance API failure: %s', exc)
        print(f'FAILURE: Binance API error -> {exc}')
        return 3
    except BinanceRequestError as exc:
        logger.error('Request failure: %s', exc)
        print(f'FAILURE: network/request error -> {exc}')
        return 4
    except Exception as exc:  # pragma: no cover
        logger.exception('Unexpected error: %s', exc)
        print(f'FAILURE: unexpected error -> {exc}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
