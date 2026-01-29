from app.db.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

    def cursor(self):
        return self.conn.cursor(dictionary=True)

    def commit(self):
        self.conn.commit()
