from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import Restaurant, MenuCategory, Customers, PreOrder, OrderItem, MenuItem, MenuTag

db = SQLAlchemy()
from config import Config

def create_app():
    app = Flask(__name__)

    app.secret_key = "dev"

    app.config.from_object(Config)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    db.init_app(app)

    # Create tables
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()

    return app


# ----------------------------
# Seed example data
# ----------------------------
def seed_data():
    if Restaurant.query.first():  # prevent duplicate seeding
        return

    # --- Restaurants ---
    resto = Restaurant(name="My Delhi Newcastle", email="admin@resto.com", password="1234")
    db.session.add(resto)
    db.session.commit()

    # --- Menu Categories ---
    drinks = MenuCategory(name="Drinks", restaurant_id=resto.id)
    food = MenuCategory(name="Food", restaurant_id=resto.id)
    db.session.add_all([drinks, food])
    db.session.commit()

    # --- Subcategories ---
    cocktails = MenuCategory(name="Cocktails", restaurant_id=resto.id, parent=drinks)
    wines = MenuCategory(name="Wines", restaurant_id=resto.id, parent=drinks)
    mocktails = MenuCategory(name="Mocktails", restaurant_id=resto.id, parent=drinks)
    brewery = MenuCategory(name="Mocktails", restaurant_id=resto.id, parent=drinks)
    soft_drinks = MenuCategory(name="Mocktails", restaurant_id=resto.id, parent=drinks)

    street_plates = MenuCategory(name="Street Plates", restaurant_id=resto.id, parent=food)
    curry = MenuCategory(name="Roadside Curries", restaurant_id=resto.id, parent=food)

    db.session.add_all([cocktails, wines, curry, street_plates, mocktails, brewery, soft_drinks])
    db.session.commit()

    # --- Menu Tags ---
    gf_tag = MenuTag(name="GF")  # gluten-free
    vegan_tag = MenuTag(name="Vegan")
    vegetarian = MenuTag(name="Vegan")
    db.session.add_all([gf_tag, vegan_tag, vegetarian])
    db.session.commit()

    # --- Menu Items ---
    goan_zombie = MenuItem(name="Goan Zombie", category=cocktails,  description="Our Goan Zombie cocktail, inspired by Bollywood, is a tropical mix of spiced and coconut rum, coconut syrup, Grenadine, and a fearless attitude.")
    rose = MenuItem(name="The Emperor´s Rose", category=cocktails,  description="A beautiful sunset-inspired cocktail of pink and red hues. A lychee delight of vodka, lychee liqueur, and rose and cardamom syrup.")
    amber = MenuItem(name="The Amber Solstice", category=cocktails, description="A silken blend of Disaronno Velvet, spiced rum, and coffee liqueur, gently lit with vanilla decadence")
    duke = MenuItem(name="Duke of Connaught", category=cocktails, description="Escape to Delhi's Connaught Place with our tropical twist on the classic mojito. A refreshing blend of pineapple rum, coconut, mint and lime.")
    highball = MenuItem(name="Karnataka Highball", category=cocktails, description="A nostalgic old Indian sweet shop blend of mango, lychee and marshmallow, evoking the charm of Karnataka's beaches.")
    bramble = MenuItem(name="Rangpur Bramble", category=cocktails, description="A divine combination of Tanqueray Rangpur gin, lemon, and blackberry liqueur, creating a perfect balance of sweet and sour flavours with a fruity essence.")
    twilight = MenuItem(name="Bollywood Twilight", category=cocktails, description="A star-studded mix of sloe gin, violet and blackberry liqueurs, apple, Indian plum and lemon juice.")
    margarita = MenuItem(name="Margarita", category=cocktails, description="A classic mix of tequila, fresh lime juice, and orange liqueur, served with a mango salted rim. ")
    new_ice = MenuItem(name="New Delhi Iced Tea", category=cocktails, description="A tropical twist with mango vodka, Indian spiced rum, and classic Long Island Iced Tea elements.")
    daiquiri = MenuItem(name="New Delhi Iced Tea", category=cocktails, description="A timeless blend of rum, fresh lime juice, and simple syrup, perfectly balanced and refreshing.")

    chicken_curry = MenuItem(name="Chicken Curry", category=curry)
    chicken_curry.tags.append(gf_tag)

    margherita = MenuItem(name="Margherita Pizza", category=starter)
    margherita.tags.append(vegan_tag)

    db.session.add_all([mojito, bourbon, chicken_curry, margherita])
    db.session.commit()

    # --- Customers & Preorders ---
    customer1 = Customers(
        restaurant_id=resto.id,
        customer_name="Alice",
        code=101,
        phone="1234567890",
        email="alice@email.com",
        num_people=9,
        time="19:00"
    )
    db.session.add(customer1)
    db.session.commit()

    preorder1 = PreOrder(
        customer_id=customer1.id,
        person_name="Alice",
        notes="Please make mojito extra minty"
    )
    db.session.add(preorder1)
    db.session.commit()

    # Add items to preorder
    order_item1 = OrderItem(preorder_id=preorder1.id, menu_item_id=mojito.id)
    order_item2 = OrderItem(preorder_id=preorder1.id, menu_item_id=bourbon.id)
    db.session.add_all([order_item1, order_item2])
    db.session.commit()

    print("Database seeded successfully!")