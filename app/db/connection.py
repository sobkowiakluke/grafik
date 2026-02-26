import mysql.connector
from app.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

    def cursor(self):
        self.conn.ping(reconnect=True)
        return self.conn.cursor(dictionary=True)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
