from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.secret_key = "dev"

    app.config.from_object(Config)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    from . import models
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
    from .models import Restaurant, MenuCategory, Customers, PreOrder, OrderItem, MenuItem, MenuTag, MenuItemSize, SpiceLevel
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

    street_plates = MenuCategory(name="Street Plates", restaurant_id=resto.id, parent=food, description="Choose one mixed platter per person")
    curry = MenuCategory(name="Roadside Curries", restaurant_id=resto.id, parent=food, description="Choose one Roadside Curry per person."
                                                                                                   "Every Roadside Curry is served with Dum Pulao Rice, "
                                                                                                   "plus an assorted naan basket, signature Chacha Chips "
                                                                                                   "and a hearty Punjabi Dal Tadka for the table to share -perfect "
                                                                                                   "for a group feast!")

    db.session.add_all([cocktails, wines, curry, street_plates, mocktails, brewery, soft_drinks])
    db.session.commit()

    # --- Sub-Subcategories ---
    sparkling_wine = MenuCategory(name="Sparkling Wine", restaurant_id=resto.id, parent=wines)
    white_wine = MenuCategory(name="White Wine", restaurant_id=resto.id, parent=wines)
    red_wine = MenuCategory(name="Red Wine", restaurant_id=resto.id, parent=wines)
    rose_wine = MenuCategory(name="Rose Wine", restaurant_id=resto.id, parent=wines)

    db.session.add_all([sparkling_wine, white_wine, red_wine, rose_wine])
    db.session.commit()

    # --- Menu Tags ---
    gf_tag = MenuTag(name="GF")  # gluten-free
    vegan_tag = MenuTag(name="Vegan")
    vegetarian_tag = MenuTag(name="Vegetarian")

    db.session.add_all([gf_tag, vegan_tag, vegetarian_tag])
    db.session.commit()

    # --- Menu Spice ---
    low = SpiceLevel(level=0, label="Low")
    medium = SpiceLevel(level=1, label="Medium")
    high = SpiceLevel(level=2, label="High")

    db.session.add_all([low, high, medium])
    db.session.commit()

    # --- Menu Items ---

    # Cocktails
    goan_zombie = MenuItem(name="Goan Zombie", category=cocktails,  description="Our Goan Zombie cocktail, inspired by Bollywood, "
                                                                                "is a tropical mix of spiced and coconut rum, coconut syrup, "
                                                                                "renadine, and a fearless attitude.")
    rose = MenuItem(name="The Emperor´s Rose", category=cocktails,  description="A beautiful sunset-inspired cocktail of pink and red hues. "
                                                                                "A lychee delight of vodka, lychee liqueur, and rose and cardamom syrup.")
    amber = MenuItem(name="The Amber Solstice", category=cocktails, description="A silken blend of Disaronno Velvet, spiced rum, "
                                                                                "and coffee liqueur, gently lit with vanilla decadence")
    duke = MenuItem(name="Duke of Connaught", category=cocktails, description="Escape to Delhi's Connaught Place with our tropical twist on the "
                                                                              "classic mojito. A refreshing blend of pineapple rum, coconut, mint and lime.")
    highball = MenuItem(name="Karnataka Highball", category=cocktails, description="A nostalgic old Indian sweet shop blend of mango, lychee and "
                                                                                   "marshmallow, evoking the charm of Karnataka's beaches.")
    bramble = MenuItem(name="Rangpur Bramble", category=cocktails, description="A divine combination of Tanqueray Rangpur gin, lemon, and "
                                                                               "blackberry liqueur, creating a perfect balance of sweet and sour flavours with a fruity essence.")
    twilight = MenuItem(name="Bollywood Twilight", category=cocktails, description="A star-studded mix of sloe gin, violet and blackberry "
                                                                                   "liqueurs, apple, Indian plum and lemon juice.")
    margarita = MenuItem(name="Margarita", category=cocktails, description="A classic mix of tequila, fresh lime juice, and orange liqueur, "
                                                                           "served with a mango salted rim. ")
    new_ice = MenuItem(name="New Delhi Iced Tea", category=cocktails, description="A tropical twist with mango vodka, Indian spiced rum, "
                                                                                  "and classic Long Island Iced Tea elements.")
    daiquiri = MenuItem(name="New Delhi Iced Tea", category=cocktails, description="A timeless blend of rum, fresh lime juice, and simple"
                                                                                   " syrup, perfectly balanced and refreshing.")

    # Mocktails
    dilliwali = MenuItem(name="Dilliwali Lemonade", category=mocktails, description="A unique blend of spices, mint, lime and lemon muddled "
                                                                                    "together for our take on North India's favourite drink known as Shikanji.")
    pink = MenuItem(name="Pink Memsaab", category=mocktails, description="A rich fruity mix of berries, Indian plum and pomegranate, topped with "
                                                                         "a deliciously chilled lemonade for an exotic and energising taste.")
    ruby = MenuItem(name="Ruby Royale", category=mocktails, description="Pomegranata with a seasonal fruit mix of apple and lemon, "
                                                                        "gently lifted with cinnamon and soda.")
    dehli =  MenuItem(name="Ruby Royale", category=mocktails, description="A Pina Colada with a nod to Delhi's famous Mohabbat Ka "
                                                                          "Sharbat, coconut milk, watermelon, pineapple and a touch of rose syrup.")

    # Wines
    prosecco = MenuItem(name="Prosecco Il Castello", category=sparkling_wine, description="With a straw yellow colour and greenish reflection, "
                                                                                          "this prosecco has a subtle fruity aroma of apple, a dry "
                                                                                          "and crisp fruity taste, and a clean finish.")
    small_prosecco = MenuItemSize(menu_item=prosecco, size="175ml")
    bottle_prosecco = MenuItemSize(menu_item=prosecco, size="Bottle")

    cuvee = MenuItem(name="Laurent-Perrier La Cuvée", category=sparkling_wine, description="Laurent-Perrier's signature champagne, La Cuvée, is"
                                                                                           " delicate yet complex with crisp notes of citrus fruit "
                                                                                           "and white flowers and a great length on the finish")
    bottle_cuvve = MenuItemSize(menu_item=cuvee, size="Bottle")

    #Here is everything else goes but too much drinks :)

    db.session.add_all([goan_zombie, ruby, rose, amber, duke, highball, bramble, twilight, margarita, new_ice, daiquiri,
                        dilliwali, pink, dehli, prosecco, small_prosecco, bottle_prosecco, cuvee, bottle_cuvve ])
    db.session.commit()

    # Street plates
    veg_platter = MenuItem(name="Veg Platter", category=street_plates, description="Onion Bhaji, Cauliflower Manchurian and Panner tikka")
    veg_platter.tags.append(vegetarian_tag)

    non_platter = MenuItem(name="Veg Platter", category=street_plates, description="Delhi Chicken Tikka, Chilli Chicken, Onion Bhaji")

    vegan_platter = MenuItem(name="Vegan Platter", category=street_plates, description="Onion Bhaji, Cauliflower Manchurian and Vegetable Samosa")
    vegan_platter.tags.append(vegan_tag)

    # Curries
    railway = MenuItem(name="Railway Station Lamb Curry", category=curry, description="Mildly spiced imperial lamb curry with creamy coconut sauce, flavoured with our signature garam masala. Inspired by the pantries of Indian trains.")
    gosht = MenuItem(name="Delhi Kadhai Gosht", category=curry, description="From Punjab to Delhi, this slow-cooked lamb curry offers a delightful contrast of Punjabi spices alongside flavoursome onions and peppers cooked Delhi-style.")
    butter = MenuItem(name="Butter Chicken 1950´s", category=curry, description="Tandoori roasted chicken tikka smothered in a rich, creamy tomato sauce, embracing the authentic Delhi origins of this humble dish.")
    bhuna = MenuItem(name="Roadside Chicken Bhuna", category=curry, description="A road-style Punjabi chicken Bhuna inspired by the vibrant highways of North India.")
    fish = MenuItem(name="Fish Curry", category=curry, description="Malabar food is hugely popular in Delhi, and none more so than this. Delicately spiced fish cooked gently in a creamy coconut sauce.")

    panner = MenuItem(name="Deli Panner Butter Masala", category=curry, description="Soft Paneer cooked in a classic butter masala sauce, a popular Delhi-style curry.")
    panner.tags.append(vegetarian_tag)

    grandma = MenuItem(name="Grandma´s Aloo Mataar", category=curry, description="A family heirloom passed down from my dear Grandma, a traditional North Indian potato and pea curry.")
    grandma.tags.append(vegan_tag)

    tawa = MenuItem(name="Panner Tawa Bhuna", category=curry, description="Sautéed paneer in a delightful spicy bhuna sauce, a favourite found in Delhi's roadside eateries.")
    tawa.tags.append(vegetarian_tag)

    kozhi = MenuItem(name="Kozhi Chicken Curry", category=curry, spice_level=high, description="Hailing from a seaport on the East coast of India, this spicy coconut-flavoured chicken curry is rich in tantalising spices.")


    db.session.add_all([veg_platter, non_platter, vegan_platter, railway, gosht, butter, bhuna, fish, panner, grandma, tawa, kozhi])
    db.session.commit()


    # --- Customers & Preorders ---
    customer1 = Customers(
        restaurant_id=resto.id,
        customer_name="Alice",
        code=101,
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
    order_item1 = OrderItem(preorder_id=preorder1.id, menu_item_id=goan_zombie.id)
    order_item2 = OrderItem(preorder_id=preorder1.id, menu_item_id=gosht.id)
    db.session.add_all([order_item1, order_item2])
    db.session.commit()

    print("Database seeded successfully!")