import os

class Config:
    DEBUG = False


    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///restaurant.db"
    )