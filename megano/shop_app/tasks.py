import time

from celery import shared_task
from shop_app.models import Order


@shared_task
def payment(order_pk: str, card_num: str) -> str:
    """Функция для выполнения фиктивной оплаты."""

    time.sleep(3)
    order = Order.objects.get(id=order_pk)
    if int(card_num) % 2 == 0 and not card_num.endswith("0"):
        order.status = "paid"
        order.save(update_fields=["status"])
    return order.status
