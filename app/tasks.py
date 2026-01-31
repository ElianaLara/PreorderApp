from datetime import datetime, timedelta
from .models import Customers
from . import db

def delete_old_orders():
    threshold = datetime.utcnow() - timedelta(days=30)

    orders = Customers.query.filter(
        Customers.deleted == True,
        Customers.deleted_at <= threshold
    ).all()

    for order in orders:
        db.session.delete(order)

    db.session.commit()