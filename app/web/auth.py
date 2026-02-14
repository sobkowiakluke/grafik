from flask_login import UserMixin
from app.db.connection import Database

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        db = Database()
        cur = db.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        return User(row["id"], row["username"])

    @staticmethod
    def get_by_username(username):
        db = Database()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row
