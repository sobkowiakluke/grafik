import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.connection import Database

def test_connection():
    db = Database()
    try:
        cur = db.cursor()
        cur.execute("SELECT 1 AS test")
        result = cur.fetchone()
        print("Połączenie OK:", result)
        cur.close()
    except Exception as e:
        print("Błąd połączenia:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
