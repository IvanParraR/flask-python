import uuid
from datetime import timezone
from decimal import Decimal

from ..database.database_service import DatabaseService
from .dto.create_order_dto import MAX_INT, CreateOrderDto

MAX_AMOUNT_CENTS = 9_999_999_999


class OrderLimitError(Exception):
    pass


class OrdersService:
    def __init__(self, database: DatabaseService) -> None:
        self.database = database

    def create(self, order: CreateOrderDto) -> dict:
        total_cents = sum(int(item.price * 100) * item.quantity for item in order.items)
        items_count = sum(item.quantity for item in order.items)

        if total_cents > MAX_AMOUNT_CENTS or items_count > MAX_INT:
            raise OrderLimitError("Order totals exceed the supported limits")

        order_id = str(uuid.uuid4())

        # El context manager hace BEGIN; COMMIT al salir, o ROLLBACK si hay excepción.
        with self.database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO orders (order_id, customer_id, total_amount, items_count)
                       VALUES (%s, %s, %s, %s)
                       RETURNING order_id, total_amount, items_count, created_at""",
                    (order_id, order.customer_id, Decimal(total_cents) / 100, items_count),
                )
                created = cur.fetchone()

                placeholders = ", ".join(["(%s, %s, %s, %s)"] * len(order.items))
                params: list = []
                for item in order.items:
                    params.extend(
                        (order_id, item.product_id, item.quantity, item.price)
                    )
                cur.execute(
                    f"""INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES {placeholders}""",
                    params,
                )

        created_order_id, total_amount, count, created_at = created
        return {
            "orderId": created_order_id,
            "totalAmount": float(total_amount),
            "itemsCount": count,
            "processedAt": created_at.replace(tzinfo=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
        }
