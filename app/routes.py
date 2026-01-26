from flask import render_template, redirect, url_for, session, Blueprint, flash, request
from .forms import CodeForm, PreorderForm
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
        # Base structure for category
        cat_dict = {
            "description": cat.description,
            "subcategories": {},
            "items": []
        }

        # Add menu items
        for item in cat.menu_items:
            item_dict = {
                "name": item.name,
                "description": item.description,
                "tags": [tag.name for tag in item.tags],  # iterable list
                "spice_level": item.spice_level.label if item.spice_level else None,  # string or None
                "sizes": [size.size for size in item.sizes]  # list of strings
            }
            cat_dict["items"].append(item_dict)

        # Recursively add subcategories
        for subcat in cat.subcategories:
            cat_dict["subcategories"][subcat.name] = get_subcategories(subcat)

        # Remove empty subcategories/items for clean dict
        if not cat_dict["subcategories"]:
            cat_dict.pop("subcategories")
        if not cat_dict["items"]:
            cat_dict.pop("items")

        return cat_dict

    menu_items = {}
    for category in top_categories:
        menu_items[category.name] = get_subcategories(category)

    form = PreorderForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.notes.data
        if description:
            description = description.strip()
        else:
            description = None

        items = request.form.getlist("items[]")
        print(name, description, items)





    #print(menu_items)  # Debug
    #print("!!!!!!!!!")
    return render_template("preorder.html", menu_items=menu_items, table=table, form=form)

