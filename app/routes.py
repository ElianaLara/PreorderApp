from flask import request, render_template, redirect, url_for, session, Blueprint, flash

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/preorder", methods=["GET", "POST"])
def preorder():
    return render_template("preorder.html")