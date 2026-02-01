from datetime import datetime, timedelta
from .models import Customers
from . import db
from .email import send_email




def delete_old_orders():
    threshold = datetime.utcnow() - timedelta(days=30)

    orders = Customers.query.filter(
        Customers.deleted == True,
        Customers.deleted_at <= threshold
    ).all()

    for order in orders:
        db.session.delete(order)

    db.session.commit()

def send_reminder():
    daynow = datetime.now()

    for customer in Customers.query.all():
        if not customer.day:
            continue

        preorder_day = datetime.strptime(customer.day, "%Y-%m-%d")

        if customer.status != "completed" and (0 <= (preorder_day - daynow).days <= 2):
            send_email(
                subject=f"📝 Reminder: Please Complete Your Preorder, {customer.customer_name}!",
                recipients=[customer.email],
                body="This is a reminder to complete your preorder."
            )