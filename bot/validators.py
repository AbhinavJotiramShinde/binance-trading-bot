from __future__ import annotations

from decimal import Decimal, InvalidOperation

VALID_SIDES = {'BUY', 'SELL'}
VALID_ORDER_TYPES = {'MARKET', 'LIMIT'}


class ValidationError(ValueError):
    """Raised when CLI input validation fails."""


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValidationError('symbol is required')
    symbol = symbol.strip().upper()
    if not symbol.endswith('USDT'):
        raise ValidationError('symbol must be a USDT-M pair such as BTCUSDT')
    if not symbol.isalnum():
        raise ValidationError('symbol must be alphanumeric')
    return symbol


def validate_side(side: str) -> str:
    side = (side or '').strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f'side must be one of: {", ".join(sorted(VALID_SIDES))}')
    return side


def validate_order_type(order_type: str) -> str:
    order_type = (order_type or '').strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(f'order_type must be one of: {", ".join(sorted(VALID_ORDER_TYPES))}')
    return order_type


def validate_positive_decimal(value: str | float | int, field_name: str) -> str:
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError(f'{field_name} must be a valid number')
    if decimal_value <= 0:
        raise ValidationError(f'{field_name} must be greater than 0')
    return format(decimal_value.normalize(), 'f')


def validate_price_for_order(order_type: str, price: str | None) -> str | None:
    if order_type == 'LIMIT':
        if price is None:
            raise ValidationError('price is required for LIMIT orders')
        return validate_positive_decimal(price, 'price')
    if price is not None:
        return validate_positive_decimal(price, 'price')
    return None
