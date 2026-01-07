from app.db.connection import Database
import calendar
from datetime import datetime

class ScheduleService:
    def __init__(self):
        self.db = Database()

    def create_schedule(self, year: int, month: int):
        cur = self.db.cursor()

        # ustalenie zakresu miesiąca
        last_day = calendar.monthrange(year, month)[1]
        start_dt = f"{year}-{month:02d}-01 00:00:00"
        end_dt = f"{year}-{month:02d}-{last_day} 23:59:59"

        # ustalenie kolejnej wersji
        cur.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 AS next_version FROM schedules WHERE year=%s AND month=%s",
            (year, month)
        )
        version = cur.fetchone()["next_version"]

        cur.execute(
            """INSERT INTO schedules (year, month, version, start_datetime, end_datetime)
               VALUES (%s, %s, %s, %s, %s)""",
            (year, month, version, start_dt, end_dt)
        )

        cur.close()
        print(f"Utworzono grafik: {year}-{month:02d}, wersja {version}")

    def list_schedules(self):
        cur = self.db.cursor()
        cur.execute(
            """SELECT id, year, month, version, status, start_datetime, end_datetime
               FROM schedules
               ORDER BY year DESC, month DESC, version DESC"""
        )
        data = cur.fetchall()
        cur.close()
        return data

    def get_schedule(self, schedule_id: int):
        cur = self.db.cursor()
        cur.execute(
            "SELECT * FROM schedules WHERE id = %s",
            (schedule_id,)
        )
        data = cur.fetchone()
        cur.close()
        return data

    def delete_schedule(self, schedule_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM schedules WHERE id = %s", (schedule_id,))
        cur.close()
        print(f"Usunięto grafik ID {schedule_id}")

    def update_status(self, schedule_id: int, status: str):
        if status not in ("draft", "approved", "archived"):
            print("Nieprawidłowy status.")
            return

        cur = self.db.cursor()

    # jeśli próbujemy ustawić approved
        if status == "approved":
        # sprawdzamy, czy w tym miesiącu już istnieje approved
            cur.execute(
                "SELECT id FROM schedules "
                "WHERE year=(SELECT year FROM schedules WHERE id=%s) "
                "AND month=(SELECT month FROM schedules WHERE id=%s) "
                "AND status='approved'",
                (schedule_id, schedule_id)
            )
            existing = cur.fetchone()
            if existing:
                print(f"Nie można zatwierdzić. Już istnieje approved grafiku ID {existing['id']}")
                cur.close()
                return

    # aktualizacja statusu
        cur.execute(
            "UPDATE schedules SET status = %s WHERE id = %s",
            (status, schedule_id)
        )
        cur.close()
        print(f"Zmieniono status grafiku ID {schedule_id} na '{status}'")

