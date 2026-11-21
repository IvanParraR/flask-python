from dataclasses import dataclass
from decimal import Decimal

MAX_INT = 2_147_483_647
MAX_PRICE = Decimal("99999999.99")

ORDER_FIELDS = {"customerId", "items"}
ITEM_FIELDS = {"productId", "quantity", "price"}


class ValidationError(Exception):
    def __init__(self, messages: list[str]) -> None:
        super().__init__("; ".join(messages))
        self.messages = messages


@dataclass(frozen=True)
class CreateOrderItemDto:
    product_id: str
    quantity: int
    price: Decimal


@dataclass(frozen=True)
class CreateOrderDto:
    customer_id: str
    items: list[CreateOrderItemDto]


def _is_valid_string(value: object) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= 50


def _is_valid_int(value: object) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 1 <= value <= MAX_INT
    )


def _is_valid_price(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        return False
    price = Decimal(value)
    if not price.is_finite() or not 0 <= price <= MAX_PRICE:
        return False
    return price == price.quantize(Decimal("0.01"))  # máx. 2 decimales


def parse_create_order(body: object) -> CreateOrderDto:
    """Valida el JSON (equivale al ValidationPipe whitelist/forbidNonWhitelisted)."""
    if not isinstance(body, dict):
        raise ValidationError(["body must be a JSON object"])

    errors: list[str] = []
    for extra in sorted(set(body) - ORDER_FIELDS):
        errors.append(f"property {extra} should not exist")

    customer_id = body.get("customerId")
    if not _is_valid_string(customer_id):
        errors.append("customerId must be a string between 1 and 50 characters")

    raw_items = body.get("items")
    items: list[CreateOrderItemDto] = []
    if not isinstance(raw_items, list) or len(raw_items) < 1:
        errors.append("items must be a non-empty array")
    else:
        for index, raw in enumerate(raw_items):
            prefix = f"items.{index}"
            if not isinstance(raw, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for extra in sorted(set(raw) - ITEM_FIELDS):
                errors.append(f"{prefix}.property {extra} should not exist")
            ok = True
            if not _is_valid_string(raw.get("productId")):
                errors.append(
                    f"{prefix}.productId must be a string between 1 and 50 characters"
                )
                ok = False
            if not _is_valid_int(raw.get("quantity")):
                errors.append(f"{prefix}.quantity must be an integer >= 1")
                ok = False
            if not _is_valid_price(raw.get("price")):
                errors.append(
                    f"{prefix}.price must be a number >= 0 with at most 2 decimals"
                )
                ok = False
            if ok:
                items.append(
                    CreateOrderItemDto(
                        raw["productId"], raw["quantity"], Decimal(raw["price"])
                    )
                )

    if errors:
        raise ValidationError(errors)
    return CreateOrderDto(customer_id, items)
