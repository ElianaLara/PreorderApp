from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Import models after db is initialized
    from .models import Restaurant, MenuCategory, MenuItem, Customers, PreOrder, OrderItem

    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()

        # 1. Create restaurant
        delhi = Restaurant(
            name="My Delhi Newcastle",
            email="admin@delhinewcastle.co.uk",
            password="demo"  # in real app, hash this!
        )
        db.session.add(delhi)
        db.session.commit()  # commit so delhi.id is available

        # 2. Create simplified categories
        categories = ["Starter", "Main", "Dessert", "Drink"]
        category_map = {}
        for name in categories:
            c = MenuCategory(
                name=name,
                restaurant_id=delhi.id,
                required=(name in ["Starter", "Main"])
            )
            db.session.add(c)
            db.session.commit()
            category_map[name] = c.id

        # 3. Add menu items
        menu_items = {
            "Starter": ["Veg Platter", "Non Veg Platter", "Vegan Platter"],
            "Main": ["Railway Station Lamb Curry", "Delhi Kadhai Gosht", "Butter Chicken 1950s",
                     "Roadside Chicken Bhuna", "Kozhi Chicken Curry", "South Indian Fish Curry",
                     "Dilli Paneer Butter Masala", "Grandma's Aloo Matar", "Paneer Tawa Bhuna"],
            "Dessert": ["Lotus Biscoff Cheesecake", "Gajar Halwa", "Chocolate Fudge Cake", "Chef's Gulabjamun"],
            "Drink": ["Coke", "Mango Lassi", "Goan Zombie", "Orange Juice"]
        }

        # Add menu items to DB
        item_map = {}
        for cat, items in menu_items.items():
            for item in items:
                m = MenuItem(name=item, category_id=category_map[cat], available=True)
                db.session.add(m)
                db.session.commit()
                item_map[item] = m.id

        db.session.commit()

        # 4. Add customers and preorders
        tables = [
            {
                "customer_name": "Alice Johnson",
                "code": 23449,
                "phone": "123456789",
                "email": "alice@example.com",
                "table_number": 10,
                "num_people": 8,
                "time": "19:00",
                "orders": [
                    {"person_name": "Alice", "Starter": "Veg Platter", "Main": "Butter Chicken 1950s",
                     "Dessert": "Gajar Halwa", "Drink": "Coke"},
                    {"person_name": "María", "Starter": "Non Veg Platter", "Main": "Delhi Kadhai Gosht",
                     "Dessert": "Chocolate Fudge Cake", "Drink": "Goan Zombie"}
                ]
            },
            {
                "customer_name": "Bob Smith",
                "code": 23450,
                "phone": "987654321",
                "email": "bob@example.com",
                "table_number": 10,
                "num_people": 21,
                "time": "20:00",
                "orders": [
                    {"person_name": "Bob", "Starter": "Vegan Platter", "Main": "Paneer Tawa Bhuna",
                     "Dessert": "Lotus Biscoff Cheesecake", "Drink": "Mango Lassi"}
                ]
            }
        ]

        # Add tables and preorders
        for t in tables:
            customer = Customers(
                restaurant_id=delhi.id,
                customer_name=t["customer_name"],
                code=t["code"],
                phone=t["phone"],
                email=t["email"],
                table_number=t["table_number"],
                num_people=t["num_people"],
                time=t["time"]
            )
            db.session.add(customer)
            db.session.commit()

            for o in t["orders"]:
                preorder = PreOrder(
                    customer_id=customer.id,
                    person_name=o["person_name"]
                )
                db.session.add(preorder)
                db.session.commit()

                # Add ordered items
                for cat in ["Starter", "Main", "Dessert", "Drink"]:
                    if cat in o:
                        db.session.add(OrderItem(
                            preorder_id=preorder.id,
                            menu_item_id=item_map[o[cat]]
                        ))

        db.session.commit()

        # Register blueprint
        from .routes import main
        app.register_blueprint(main)

    return app
