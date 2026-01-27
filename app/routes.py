from flask import render_template, redirect, url_for, session, Blueprint, flash, request
from .forms import CodeForm, PreorderForm, LoginForm
from .models import Customers, MenuItem, MenuCategory, PreOrder, OrderItem, MenuItemSize, Restaurant
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

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Find the restaurant by email
        restaurant = Restaurant.query.filter_by(email=email).first()

        if not restaurant:
            flash("No account found with that email.")
            return redirect(url_for('main.login'))

        # Check password (plain text)
        if restaurant.password != password:
            flash("Incorrect password.")
            return redirect(url_for('main.login'))

        # Login successful — store restaurant id in session
        session['restaurant_id'] = restaurant.id
        session['restaurant_name'] = restaurant.name
        return redirect(url_for('main.dashboard'))

    return render_template('login.html', form=form)

@main.route('/dashboard', methods=['GET', 'POST'])
#login_required
def dashboard():
    name = session.get('restaurant_name')
    restaurant = Restaurant.query.filter_by(name=name).first()
    customers = Customers.query.filter_by(restaurant_id=restaurant.id).all()

    return render_template('dashboard.html', name=name, orders=customers)


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/preorder/<int:code>', methods=['GET', 'POST'])
def preorder(code):

    #------
    #This is the Menu logic
    top_categories = MenuCategory.query.filter_by(parent_id=None).all()  # Only main categories
    table = Customers.query.filter_by(code=code).first()
    preorders = table.preorders
    preorder_completed = False

    #  preorder_completed true and send email
    if len(table.preorders) >= table.num_people:
        preorder_completed = True
        table.status="completed"
        db.session.commit()

        # Build preorder text for email
        preorder_lines = []
        preorder_lines.append("Thank you for completing your pre-order please see the order below: \n")

        for order in table.preorders:  # Loop over all preorders for this table
            lines = []  # Lines for this person
            lines.append(f"{order.person_name}:")  # Person's name on its own line

            for item in order.items:
                if item.menu_item:
                    parts = []

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


    # Menu logic
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

    #When a new order is submiteed logic
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
        items = request.form.getlist("items[]")  # e.g. ["Curry - Large", "Wine - Bottle"]

        if not items:
            flash("Please add at least one item")
            return redirect(url_for("main.preorder", code=code))

        # --- Check required categories/subcategories ---
        # Get all top-level required categories for this restaurant
        required_cats = MenuCategory.query.filter_by(restaurant_id=table.restaurant_id, required=True).all()

        # Build a set of category IDs from submitted items
        submitted_cat_ids = set()
        for item_text in items:
            item_name = item_text.split(" - ")[0].strip()
            menu_item = MenuItem.query.filter_by(name=item_name).first()
            if menu_item:
                submitted_cat_ids.add(menu_item.category_id)

        # Function to get all subcategory names that are required but missing
        def get_missing_required_subcats(cat):
            missing = []
            # If this category itself is required and not submitted
            if cat.required and cat.id not in submitted_cat_ids:
                missing.append(cat.name)
            # Check recursively for subcategories
            for subcat in cat.subcategories:
                missing += get_missing_required_subcats(subcat)
            return missing

        # Collect all missing required subcategories
        missing_required = []
        for cat in required_cats:
            missing_required += get_missing_required_subcats(cat)

        if missing_required:
            flash(f"You must select an item from the required categories: {', '.join(missing_required)}")
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
            parts = item_text.split(" - ")
            item_name = parts[0].strip()
            size_name = parts[1].strip() if len(parts) > 1 else None

            menu_item = MenuItem.query.filter_by(name=item_name).first()
            size_obj = None
            if menu_item and size_name:
                size_obj = MenuItemSize.query.filter_by(menu_item_id=menu_item.id, size=size_name).first()

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

