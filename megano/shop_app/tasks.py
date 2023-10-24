import time

from celery import Celery, shared_task

from shop_app.models import Order

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@shared_task
def payment(order_id, card_num):
    print(111)
    time.sleep(3)
    if int(card_num) % 2 == 0 and not card_num.endswith('0'):
        print(222)
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save(update_fields=['status'])


