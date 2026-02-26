from flask import g
from app.db.connection import Database


def get_db():
    if "db" not in g:
        g.db = Database()
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
