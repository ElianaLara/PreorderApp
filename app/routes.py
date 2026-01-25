from flask import render_template, redirect, url_for, session, Blueprint, flash
from .forms import CodeForm
from .models import Customers, MenuItem, MenuCategory, PreOrder

main = Blueprint("main", __name__)



@main.route('/', methods=['GET', 'POST'])
def home():
    form = CodeForm()
    if form.validate_on_submit():
        user_code = form.code.data

        # Check if the code exists in the database
        table = Customers.query.filter_by(code=user_code).first()
        if table:
            flash(f'Code {user_code} is valid! Redirecting to preorder...')

            return redirect(url_for('main.preorder', code=user_code))

        else:
            # Code is invalid
            flash(f'Code {user_code} is not valid. Please try again.')
            return redirect(url_for('main.home'))

    return render_template('home.html', form=form)


@main.route('/preorder/<int:code>', methods=['GET', 'POST'])
def preorder(code):
    top_categories = MenuCategory.query.filter_by(parent_id=None).all()  # Only main categories
    table = Customers.query.filter_by(code=code).first()

    def get_subcategories(cat):
        sub_dict = {}
        if cat.subcategories:
            for subcat in cat.subcategories:
                # Recursively build subcategories
                sub_dict[subcat.name] = get_subcategories(subcat) or [
                    {"name": item.name, "description": item.description} for item in subcat.menu_items
                ]
            return sub_dict
        else:
            # No subcategories, return list of dicts with name & description
            return [{"name": item.name, "description": item.description} for item in cat.menu_items]

    menu_items = {}
    for category in top_categories:
        menu_items[category.name] = get_subcategories(category)

    print(menu_items)  # Debug
    return render_template("preorder.html", menu_items=menu_items, table=table)