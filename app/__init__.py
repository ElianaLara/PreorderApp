from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.secret_key = "dev"

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)



    return app