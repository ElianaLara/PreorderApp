from flask import render_template, redirect, url_for, session, Blueprint, flash, request
from .forms import CodeForm, PreorderForm
from .models import Customers, MenuItem, MenuCategory, PreOrder, OrderItem, MenuItemSize
from . import db
from .email import send_email

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
    preorder_completed = False

    # If table doesn’t exist, redirect
    if not table:
        flash("Table not found")
        return redirect(url_for("main.home"))

    #  preorder_completed true and send email
    if len(table.preorders) >= table.num_people:
        preorder_completed = True

        # Build preorder text for email
        preorder_lines = []
        preorder_lines.append("Thank you for completing your pre-order please see the order below: \n")

        for order in table.preorders:  # Loop over all preorders for this table
            lines = []  # Lines for this person
            lines.append(f"{order.person_name}:")  # Person's name on its own line

            for item in order.items:
                if item.menu_item:
                    parts = []

                    # Parent category if exists
                    if item.menu_item.category.parent:
                        parts.append(f"{item.menu_item.category.parent.name}:")

                    # Current category
                    parts.append(f"{item.menu_item.category.name}:")

                    # Item name
                    parts.append(item.menu_item.name)

                    # Size if exists
                    if item.size:
                        parts.append(f"- {item.size.size}")

                    # Join parts for this item and add to person's lines
                    lines.append(" ".join(parts))

            # Add notes if they exist
            if order.notes:
                lines.append(f"Notes: {order.notes}")

            # Add an empty line between people
            preorder_lines.append("\n".join(lines))
            preorder_lines.append("")  # Blank line for spacing

        # Join everything for email body
        email_body = "\n".join(preorder_lines)

        # Send email
        send_email(
            subject=f"🎉 Preorder Completed for {table.customer_name, }!!",
            recipients=[table.email],
            body=email_body
        )

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
        name = form.name.data.strip() if form.name.data else None

        existing_preorder = PreOrder.query.filter_by(
            customer_id=table.id,
            person_name=name
        ).first()

        if existing_preorder:
            flash(f"An order for '{name}' already exists.")
            return redirect(url_for("main.preorder", code=code))

        if not name:
            flash("Please enter your name")
            return redirect(url_for("main.preorder", code=code))
        notes = form.notes.data.strip() if form.notes.data else None
        items = request.form.getlist("items[]")

        if not items:
            flash("Please add at least one item")
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

    return render_template(
        "preorder.html",
        menu_items=menu_items,
        table=table,
        form=form,
        preorders=preorders,
        preorder_completed=preorder_completed
    )


@main.route("/preorder/<int:preorder_id>/delete", methods=["POST"])
def delete_preorder(preorder_id):
    preorder = PreOrder.query.get_or_404(preorder_id)
    db.session.delete(preorder)
    db.session.commit()
    flash("Order deleted")
    return redirect(request.referrer)

