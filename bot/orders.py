from __future__ import annotations

from typing import Any, Dict

from bot.client import BinanceFuturesClient
from bot.validators import (
    validate_order_type,
    validate_positive_decimal,
    validate_price_for_order,
    validate_side,
    validate_symbol,
)


def build_order_payload(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> Dict[str, Any]:
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_quantity = validate_positive_decimal(quantity, 'quantity')
    validated_price = validate_price_for_order(validated_type, price)

    payload: Dict[str, Any] = {
        'symbol': validated_symbol,
        'side': validated_side,
        'type': validated_type,
        'quantity': validated_quantity,
        'newOrderRespType': 'RESULT',
    }

    if validated_type == 'LIMIT':
        payload['timeInForce'] = 'GTC'
        payload['price'] = validated_price

    return payload


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> Dict[str, Any]:
    payload = build_order_payload(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )
    return client.create_order(**payload)
