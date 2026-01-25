from flask import Blueprint, render_template

main = Blueprint("main", __name__)

menu_items = {
    "Starter": ["Veg Platter", "Non Veg Platter", "Vegan Platter"],
    "Main": [
        "Railway Station Lamb Curry",
        "Delhi Kadhai Gosht",
        "Butter Chicken 1950s",
        "Roadside Chicken Bhuna",
        "Kozhi Chicken Curry",
        "South Indian Fish Curry",
        "Dilli Paneer Butter Masala",
        "Grandma's Aloo Matar",
        "Paneer Tawa Bhuna"
    ],
    "Dessert": [
        "Lotus Biscoff Cheesecake",
        "Gajar Halwa",
        "Chocolate Fudge Cake",
        "Chef's Gulabjamun"
    ],
    "Drink": ["Coke", "Mango Lassi", "Goan Zombie", "Orange Juice"]
}

@main.route("/")
def home():
    return render_template("preorder.html", menu_items=menu_items)
