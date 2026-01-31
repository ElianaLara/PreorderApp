from datetime import datetime, timedelta
from yourapp import db, create_app
from yourapp.models import Order

app = create_app()

def delete_old_orders():
    with app.app_context():
        threshold = datetime.utcnow() - timedelta(days=30)

        orders = Order.query.filter(
            Order.deleted == True,
            Order.deleted_at <= threshold
        ).all()

        for order in orders:
            db.session.delete(order)

        db.session.commit()
