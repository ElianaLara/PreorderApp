from flask import render_template, redirect, url_for, session, Blueprint, flash, request
from .forms import CodeForm, PreorderForm
from .models import Customers, MenuItem, MenuCategory, PreOrder, OrderItem, MenuItemSize
from . import db

main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    form = CodeForm()
    if form.validate_on_submit():
        user_code = form.code.data

        # Check if the code exists in the database
        table = Customers.query.filter_by(code=user_code).first()
        if table:

            return redirect(url_for('main.preorder', code=user_code))

        else:
            # Code is invalid
            flash(f'Code {user_code} is not valid. Please try again.')
            return redirect(url_for('main.home'))


    return render_template('home.html', form=form)


@main.route('/preorder/<int:code>', methods=['GET', 'POST'])
def preorder(code):

    #------
    #This is the Menu logic
    top_categories = MenuCategory.query.filter_by(parent_id=None).all()  # Only main categories
    table = Customers.query.filter_by(code=code).first()
    preorders = table.preorders

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

    # print(menu_items)  # Debug
    # print("!!!!!!!!!")

    #------
    # This is the forms logic
    form = PreorderForm()

    if form.validate_on_submit():
        name = form.name.data
        notes = form.notes.data.strip() if form.notes.data else None
        items = request.form.getlist("items[]")

        if not items:
            flash("Please add at least one item and your name")
            return redirect(url_for("main.preorder", code=code))

        # ---- Save to DB ----
        preorder = PreOrder(
            customer_id=table.id,
            person_name=name,
            notes=notes
        )
        db.session.add(preorder)
        db.session.commit()  # Commit first to get preorder.id

        # Add items
        for item_text in items:
            # Example: "Wine - Bottle" or "Curry - Large"
            parts = item_text.split(" - ")
            item_name = parts[0].strip()  # "Wine" or "Curry"
            size_name = parts[1].strip() if len(parts) > 1 else None  # "Bottle" or "Large"

            # Find the MenuItem
            menu_item = MenuItem.query.filter_by(name=item_name).first()
            size_obj = None

            if menu_item and size_name:
                # Match size exactly from MenuItemSize
                size_obj = MenuItemSize.query.filter_by(
                    menu_item_id=menu_item.id,
                    size=size_name
                ).first()

            if menu_item:
                order_item = OrderItem(
                    preorder_id=preorder.id,
                    menu_item_id=menu_item.id,
                    menu_item_size_id=size_obj.id if size_obj else None
                )
                db.session.add(order_item)

        db.session.commit()
        flash("Pre-order added successfully!")
        return redirect(url_for("main.preorder", code=code))


    return render_template("preorder.html", menu_items=menu_items, table=table, form=form, preorders=preorders)

