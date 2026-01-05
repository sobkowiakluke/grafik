import mysql.connector
from mysql.connector import Error
from app.db.config import DB_CONFIG


class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection and self.connection.is_connected():
            return self.connection
        try:
            self.connection = mysql.connector.connect(
                autocommit=True,
                **DB_CONFIG
            )
            return self.connection
        except Error as e:
            raise RuntimeError(f"Błąd połączenia z bazą: {e}")

    def cursor(self):
        return self.connect().cursor(dictionary=True)

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
