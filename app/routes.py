from flask import request, render_template, redirect, url_for, session, Blueprint, flash, abort
from .forms import CodeForm, PreorderForm, LoginForm, CostumerForm
from .models import Customers, PreOrder, MenuItem, MenuCategory, OrderItem, Restaurant
from . import db
import random
from datetime import datetime


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        ...

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
        return redirect(url_for('main.dashboard'))  # change to your dashboard route

    return render_template('login.html', form=form)

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/create_preorder', methods=['GET', 'POST'])
def create_preorder():
    form = CostumerForm()

    if form.validate_on_submit():
        code = random.randint(10000, 99999)
        while Customers.query.filter_by(code=code).first():
            code = random.randint(10000, 99999)

        time_str = form.time.data.strftime("%H:%M")  # convert to string like "18:52"
        print(time_str)

        new_customer = Customers(
            restaurant_id=session['restaurant_id'],
            customer_name=form.name.data,
            code=random.randint(10000, 99999),
            phone=str(form.phone.data),
            email=form.email.data,
            table_number=form.table_number.data,
            num_people=form.num_people.data,
            time=time_str  # <-- make sure this is a string, not datetime.time
        )

        db.session.add(new_customer)
        db.session.commit()
        form = CostumerForm()  # create a fresh form
        flash('Customer added successfully!', 'success')
        return redirect(url_for('main.view_customers'))

    return render_template('create_preorder.html', form=form)


@main.route('/customers')
def view_customers():
    customers = Customers.query.all()
    return render_template('view_customers.html', customers=customers)


@main.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    form = CostumerForm()

    if request.method == 'GET':
        form.name.data = customer.customer_name   # map model field to form
        form.phone.data = customer.phone
        form.email.data = customer.email
        form.table_number.data = customer.table_number
        form.num_people.data = customer.num_people
        # Convert string to time object
        form.time.data = datetime.strptime(customer.time, "%H:%M").time()

    if form.validate_on_submit():
        # Update the model from form data
        customer.customer_name = form.name.data
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.table_number = form.table_number.data
        customer.num_people = form.num_people.data
        customer.time = form.time.data.strftime("%H:%M")

        db.session.commit()
        flash("Customer updated successfully")
        return redirect(url_for('main.view_customers'))

    return render_template('edit_customer.html', form=form)

@main.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash("Pre-order deleted successfully.")
    return redirect(url_for('main.view_customers'))


@main.route('/code', methods=['GET', 'POST'])
def code():
    form = CodeForm()
    if form.validate_on_submit():
        user_code = form.code.data

        # Check if the code exists in the database
        table = Customers.query.filter_by(code=user_code).first()
        if table:
            flash(f'Code {user_code} is valid! Redirecting to preorder...')
            restaurant = session.get('restaurant_name')

            if not restaurant:
                return redirect(url_for('main.preorder', code=user_code))
            else:
                return redirect(url_for('main.manage_preorder', code=user_code))

        else:
            # Code is invalid
            flash(f'Code {user_code} is not valid. Please try again.')
            return redirect(url_for('main.code'))

    return render_template('code.html', form=form)


@main.route('/preorder/<int:code>', methods=['GET', 'POST'])
def preorder(code):
    table = Customers.query.filter_by(code=code).first()
    if not table:
        flash(f"No reservation found for code {code}")
        return redirect(url_for('main.code'))

    form = PreorderForm()

    # Only include Starter, Main, Dessert, and Drink
    form.starter.choices = [(None, "— No starter —")] + [
        (i.id, i.name) for i in MenuItem.query.join(MenuCategory)
        .filter(MenuCategory.name == "Starter").all()
    ]
    form.main.choices = [(None, "— No main —")] + [
        (i.id, i.name) for i in MenuItem.query.join(MenuCategory)
        .filter(MenuCategory.name == "Main").all()
    ]
    form.dessert.choices = [(None, "— No dessert —")] + [
        (i.id, i.name) for i in MenuItem.query.join(MenuCategory)
        .filter(MenuCategory.name == "Dessert").all()
    ]
    form.drink.choices = [(None, "— No drink —")] + [
        (i.id, i.name) for i in MenuItem.query.join(MenuCategory)
        .filter(MenuCategory.name == "Drink").all()
    ]

    if form.validate_on_submit():
        preorder = PreOrder(
            customer_id=table.id,
            person_name=form.person_name.data,
            notes=form.notes.data
        )
        db.session.add(preorder)
        db.session.commit()

        for item_id in (form.starter.data, form.main.data, form.dessert.data, form.drink.data):
            if item_id is not None:
                db.session.add(OrderItem(preorder_id=preorder.id, menu_item_id=item_id))

        db.session.commit()
        flash(f"Preorder for {form.person_name.data} added successfully!")
        return redirect(url_for('main.preorder', code=code))

    return render_template('preorder.html', form=form, table=table, preorders=table.preorders, restaurant= session)


@main.route('/preorder/edit/<int:preorder_id>', methods=['GET', 'POST'])
def edit_preorder(preorder_id):
    preorder = PreOrder.query.get_or_404(preorder_id)
    form = PreorderForm(obj=preorder)

    # Only use Starter, Main, Dessert, and Drink
    form.starter.choices = [(str(i.id), i.name) for i in MenuItem.query.join(MenuCategory)
                            .filter(MenuCategory.name == "Starter").all()]
    form.main.choices = [(str(i.id), i.name) for i in MenuItem.query.join(MenuCategory)
                         .filter(MenuCategory.name == "Main").all()]
    form.dessert.choices = [(str(i.id), i.name) for i in MenuItem.query.join(MenuCategory)
                            .filter(MenuCategory.name == "Dessert").all()]
    form.drink.choices = [(str(i.id), i.name) for i in MenuItem.query.join(MenuCategory)
                          .filter(MenuCategory.name == "Drink").all()]

    # Pre-fill form with current items
    if request.method == 'GET':
        items_dict = {}
        for item in preorder.items:
            category = MenuCategory.query.get(item.menu_item.category_id)
            items_dict[category.name] = str(item.menu_item_id)
        form.starter.data = items_dict.get("Starter")
        form.main.data = items_dict.get("Main")
        form.dessert.data = items_dict.get("Dessert")
        form.drink.data = items_dict.get("Drink")

    if form.validate_on_submit():
        preorder.person_name = form.person_name.data
        preorder.notes = form.notes.data
        db.session.commit()

        # Delete old order items
        OrderItem.query.filter_by(preorder_id=preorder.id).delete()

        # Add new order items
        for field_name in ["starter", "main", "dessert", "drink"]:
            menu_item_id = getattr(form, field_name).data
            if menu_item_id:
                db.session.add(OrderItem(
                    preorder_id=preorder.id,
                    menu_item_id=int(menu_item_id)
                ))

        db.session.commit()
        flash(f"Preorder for {preorder.person_name} updated!")
        return redirect(url_for('main.preorder', code=preorder.customer.code))

    return render_template('edit_preorder.html', form=form, preorder=preorder)




@main.route('/delete_preorder/<int:preorder_id>', methods=['POST'])
def delete_preorder(preorder_id):
    preorder = PreOrder.query.get_or_404(preorder_id)
    # Delete related order items
    OrderItem.query.filter_by(preorder_id=preorder.id).delete()
    db.session.delete(preorder)
    db.session.commit()
    flash('Preorder deleted successfully.')
    return redirect(request.referrer or url_for('main.home'))


@main.route('/see_preorder/<int:code>')
def see_preorder(code):
    # Get the customer by code
    customer = Customers.query.filter_by(code=code).first_or_404()

    # Get all preorders for this customer
    preorders = PreOrder.query.filter_by(customer_id=customer.id).all()

    return render_template('see_preorder.html', customer=customer, preorders=preorders)


@main.route('/manage_preorder/<int:code>')
def manage_preorder(code):
    customer = Customers.query.filter_by(code=code).first_or_404()

    # Load all categories for this restaurant
    categories = MenuCategory.query.filter_by(
        restaurant_id=customer.restaurant_id
    ).all()

    # Create empty summary dict from DB categories
    summary = {cat.name: {} for cat in categories}

    # Build live counts from preorders
    for preorder in customer.preorders:
        for order_item in preorder.items:
            item = order_item.menu_item
            category_name = MenuCategory.query.get(item.category_id).name

            summary[category_name][item.name] = (
                summary[category_name].get(item.name, 0) + 1
            )

    return render_template(
        'manage_preorder.html',
        customer=customer,
        preorders=customer.preorders,
        category_items=summary   #Summary
    )


@main.route('/logout')
def logout():
    # Clear the session
    session.pop('restaurant_id', None)
    session.pop('restaurant_name', None)

    flash("You have been logged out.", "success")
    return redirect(url_for('main.login'))
