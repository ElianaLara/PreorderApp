from flask import render_template, redirect, url_for, session, Blueprint, flash
from .forms import CodeForm
from .models import Customers

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


@main.route('/', methods=['GET', 'POST'])
def home():
    form = CodeForm()
    if form.validate_on_submit():
        user_code = form.code.data

        # Check if the code exists in the database
        table = Customers.query.filter_by(code=user_code).first()
        if table:
            flash(f'Code {user_code} is valid! Redirecting to preorder...')

            #return redirect(url_for('main.manage_preorder', code=user_code))
            return render_template("preorder.html")

        else:
            # Code is invalid
            flash(f'Code {user_code} is not valid. Please try again.')
            return redirect(url_for('main.home'))

    return render_template('home.html', form=form)
