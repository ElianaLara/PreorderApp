from . import db

#  Association table for menuItem  and menuTag
menu_item_tags = db.Table(
    'menu_item_tags',
    db.Column('menu_item_id', db.Integer, db.ForeignKey('menu_items.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('menu_tags.id'), primary_key=True)
)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    customers = db.relationship('Customers', backref='restaurant', lazy=True)
    menu_categories = db.relationship('MenuCategory', backref='restaurant', lazy=True)

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    customer_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120))
    num_people = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(5), nullable=False)

    preorders = db.relationship(
        'PreOrder',
        backref='customer',
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True
    ) #When a costumer is deleted everything is deleted

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

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    preorder_id = db.Column(db.Integer, db.ForeignKey('preorders.id'), nullable=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)


class MenuCategory(db.Model):
    __tablename__ = 'menu_categories'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable= True)
    #Self-referencing for subcategories
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=True)
    subcategories = db.relationship(
        'MenuCategory',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True
    )

    menu_items = db.relationship('MenuItem', backref='category', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text) #Description
    tags = db.relationship(
        "MenuTag",
        secondary=menu_item_tags,
        backref=db.backref("menu_items", lazy="dynamic")
    )
    spice_level_id = db.Column(db.Integer, db.ForeignKey('spice_levels.id'))
    spice_level = db.relationship("SpiceLevel", backref="menu_items")



class MenuTag(db.Model):
    __tablename__ = 'menu_tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  #"GF", "Vegan"

class MenuItemSize(db.Model):
    __tablename__ = "menu_item_sizes"
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"))
    size = db.Column(db.String, nullable=False)

    __table_args__ = (db.UniqueConstraint("menu_item_id", "size", name="uq_menuitem_size"),)

    menu_item = db.relationship("MenuItem", backref="sizes")

class SpiceLevel(db.Model):
    __tablename__ = 'spice_levels'

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)  # 0–3
    label = db.Column(db.String(50))  # Mild, Medium, Hot