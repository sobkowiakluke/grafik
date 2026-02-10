from calendar import monthrange
from datetime import datetime, timedelta
from app.db.connection import Database
from app.services.schedule_day_service import ScheduleDayService
from datetime import date, datetime, timedelta

class ScheduleService:
    def __init__(self, db, day_service):
        self.db = db
        self.day_service = day_service

    def create_schedule(self, year: int, month: int):
        last_day = monthrange(year, month)[1]  # liczba dni w miesiącu
        start_dt = datetime(year, month, 1, 0, 0, 0)
        end_dt = datetime(year, month, last_day, 23, 59, 59)

        cur = self.db.cursor()

        cur.execute(
            "SELECT MAX(version) AS max_v FROM schedules WHERE year=%s AND month=%s",
            (year, month)
        )
        row = cur.fetchone()

        if row["max_v"] is None:
            version = 1
        else:
            version = row["max_v"] + 1

        cur.execute(
            "INSERT INTO schedules (year, month, version, status, start_datetime, end_datetime) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (year, month, version, 'draft', start_dt, end_dt)
        )

        schedule_id = cur.lastrowid  # <--- Pobranie ID nowego grafiku
        self.db.commit()

        # Tworzymy dni grafiku
        for day_num in range(1, last_day + 1):
            self.day_service.add_day(schedule_id, day_num)  # <-- przekazujemy INT
        cur.close()
        print(f"Grafik dla {year}-{month:02d} został utworzony. ID grafiku: {schedule_id}")


    def delete_schedule(self, schedule_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM schedule_days WHERE schedule_id=%s", (schedule_id,))
        cur.execute("DELETE FROM schedules WHERE id=%s", (schedule_id,))
        self.db.commit()
        cur.close()
        print("Grafik usunięty.")

    def list_schedules(self):
        cur = self.db.cursor()
        cur.execute(
            "SELECT id, year, month, version, status, start_datetime, end_datetime "
            "FROM schedules ORDER BY year DESC, month DESC"
        )
        rows = cur.fetchall()
        cur.close()
        return rows

    def get_schedule(self, schedule_id: int):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM schedules WHERE id=%s", (schedule_id,))
        row = cur.fetchone()
        cur.close()
        return row
