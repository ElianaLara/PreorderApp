from flask import render_template, redirect, url_for, session, Blueprint, flash, request
from .forms import CodeForm, PreorderForm, LoginForm, CostumerForm
from .models import Customers, MenuItem, MenuCategory, PreOrder, OrderItem, MenuItemSize, Restaurant
from . import db
from .email import send_email
import random
from datetime import datetime

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
    customers = Customers.query.filter_by(
        restaurant_id=restaurant.id,
        deleted=False
    ).all()
    active_tab = request.args.get('tab', 'orders')
    preorders = (
        Customers.query
        .join(PreOrder)
        .filter(
            Customers.restaurant_id == restaurant.id,
            Customers.deleted == False
        )
        .all()
    )
    form = CostumerForm()

    if form.validate_on_submit():
        # generate unique code
        code = random.randint(10000, 99999)
        while Customers.query.filter_by(code=code).first():
            code = random.randint(10000, 99999)

        day_str = form.date.data.strftime("%d/%m/%Y")
        time_str = form.time.data.strftime("%H:%M")

        new_customer = Customers(
            restaurant_id=session['restaurant_id'],
            customer_name=form.name.data,
            code=code,
            email=form.email.data,
            num_people=form.num_people.data,
            day=day_str,
            time=time_str
        )

        db.session.add(new_customer)
        db.session.commit()

        flash('Customer added successfully! Email was sent', 'success')
        send_email(
            subject=f"Hi!! Preorder code",
            recipients=[new_customer.email],
            body=f"Your pre-order link has been generated please complete it 2 days before your reservation your code is {new_customer.code}"
        )
        return redirect(url_for('main.dashboard'))

    return render_template('dashboard.html', name=name, orders=customers, active_tab=active_tab, preorders=preorders, form=form)

@main.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Customers.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    if order.status == "approved":
        send_email(
            subject=f"🎉 Preorder Confirmed and approved for {order.customer_name,}!!",
            recipients=[order.email],
            body="Your order has been approved"
        )
        flash("An email of confirmation has been sent.")

    return redirect(url_for('main.dashboard', tab='orders'))

@main.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    order = Customers.query.get_or_404(order_id)
    order.deleted = True
    order.deleted_at = datetime.utcnow().date()
    db.session.commit()
    flash("Pre-order deleted successfully.")
    return redirect(url_for('main.dashboard', tab='orders'))

@main.route('/trash')
def trash():
    flash("Orders in the bin get automatically deleted after 30 days")
    name = session.get('restaurant_name')
    orders = Customers.query.filter_by(deleted=True).all()
    return render_template('trash.html', orders=orders, name=name)

@main.route('/restore/<int:id>', methods=['POST'])
def restore_order(id):
    order = Customers.query.get_or_404(id)
    order.deleted = False
    db.session.commit()
    return redirect(url_for('main.dashboard', tab='orders'))


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

@main.route('/view_preorder/<int:code>')
def view_preorder(code):
    name = session.get('restaurant_name')

    # Get the customer by code
    customer = Customers.query.filter_by(code=code).first_or_404()

    # Get all preorders for this customer
    preorders = PreOrder.query.filter_by(customer_id=customer.id).all()

    return render_template('view_preorder.html', customer=customer, preorders=preorders, name=name)


@main.route('/print/kitchen/<int:customer_id>')
def print_kitchen(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    preorders = PreOrder.query.filter_by(customer_id=customer.id).all()
    name = session.get('restaurant_name')

    summary = aggregate_items(preorders)
    return render_template(
        'print_orders.html',
        customer=customer,
        preorders=preorders,
        section="Kitchen",
        name=name,
        summary=summary
    )


@main.route('/edit_preorder/<int:code>', methods=['GET', 'POST'])
def edit_preorder(code):
    name = session.get('restaurant_name')

    # Get customer by code
    customer = Customers.query.filter_by(code=code).first_or_404()

    # Handle form submission
    if request.method == "POST":
        # Update customer details
        customer.customer_name = request.form.get("customer_name")
        customer.email = request.form.get("email")
        customer.num_people = request.form.get("num_people")
        customer.day = request.form.get("day")
        customer.time = request.form.get("time")

        db.session.commit()
        flash("Customer and preorders updated successfully!", "success")
        return redirect(url_for("main.edit_preorder", code=code))

    return render_template(
        "edit_preorder.html",
        customer=customer,
        name=name
    )

@main.route('/print/bar/<int:customer_id>')
def print_bar(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    preorders = PreOrder.query.filter_by(customer_id=customer.id).all()
    name = session.get('restaurant_name')

    summary = aggregate_items(preorders)
    return render_template(
        'print_orders.html',
        customer=customer,
        preorders=preorders,
        section="Bar",
        name=name,
        summary=summary
    )



def aggregate_items(preorders):
    """
    Returns a list of dicts: [{'name': ..., 'category': ..., 'quantity': ...}, ...]
    """
    counts = {}
    for order in preorders:
        for item in order.items:
            if not item.menu_item:
                continue
            key = item.menu_item.name
            if key not in counts:
                counts[key] = {
                    'name': item.menu_item.name,
                    'category': f"{item.menu_item.category.parent.name} / {item.menu_item.category.name}",
                    'quantity': 1
                }
            else:
                counts[key]['quantity'] += 1
    return list(counts.values())