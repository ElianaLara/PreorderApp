from . import db

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    customers = db.relationship('Customers', backref='restaurant', lazy=True)
    categories = db.relationship('MenuCategory', backref='restaurant', lazy=True)

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    customer_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    table_number = db.Column(db.Integer, nullable=False)
    num_people = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(5), nullable=False)

    preorders = db.relationship(
        'PreOrder',
        backref='customer',
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class PreOrder(db.Model):
    __tablename__ = 'preorders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id', ondelete="CASCADE"),  # important!
        nullable=False
    )
    person_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    items = db.relationship('OrderItem', backref='preorder', lazy=True)

class MenuCategory(db.Model):
    __tablename__ = 'menu_categories'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    name = db.Column(db.String(50), nullable=True)
    required = db.Column(db.Boolean, default=False)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)

    # Future improvements
    price = db.Column(db.Float)
    available = db.Column(db.Boolean, default=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    preorder_id = db.Column(db.Integer, db.ForeignKey('preorders.id'), nullable=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)

    menu_item = db.relationship('MenuItem')