# 🍽️ Pre-Order Web Application

A web-based pre-order system designed for restaurants to collect customer orders in advance. The app allows restaurants to manage customers and their pre-orders efficiently, improving organization, reducing errors, and saving time during service.

This project is **partially completed** and currently focuses on core functionality rather than final security and roles polish.

---

## ✨ Features

* Create customers with a unique **pre-order code**
* Collect customer details (name, email, number of people, date & time)
* Add multiple pre-ordered items per customer
* Optional **notes** per item (e.g. allergies, preferences)
* Automatic **email confirmation, completition, approval and reminder** sent to customers before, during and after pre-order submission
* Basic **analytics dashboard** for restaurants (stats of preorder status)
* View and edit existing pre-orders
* Print-friendly order summary view for bar and restaurant
* Session-based restaurant handling

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite (via SQLAlchemy ORM)
* **Frontend:** HTML, CSS

## 🚀 Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd preorder_app
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\\Scripts\\activate   # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root with your email configuration:

   ```env
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

5. **Run the application**

   ```bash
   flask run
   ```

6. Open your browser at:

   ```
   http://127.0.0.1:5000
   ```

---

## 🚀 Live pre-view

https://preorderapp.onrender.com/


## 🧠 How It Works

1. A restaurant creates a customer entry.
2. The system generates a **unique code** for that customer and sends email to costumer.
3. The customer (or staff) adds pre-ordered items linked to that code.
4. Orders can be reviewed, edited, and printed before service.
5. Customers automatically receive email of approval.
6. Restaurants can view basic analytics on preorders.

---

## ⚠️ Current Limitations

* Authentication is basic / session-based
* Analytics can be optimice 
* No role-based access (admin vs staff)
* No basic encryptation

---

## 🔮 Future Improvements

* User authentication & roles
* Advanced analytics (exports, trends and suggestions)
* Add basics of security
* Better mobile responsiveness

---

## 👩‍💻 Author

**Eliana Lara Espinosa**
Computer Science student – Newcastle University

---

## 📄 License / Disclaimer

This project is for educational purposes. Any restaurant names, menus, or branding used are **fictional or anonymised**. Sensitive configuration (like email passwords) is handled via environment variables.
