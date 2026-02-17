from calendar import monthrange
from datetime import datetime, date
from app.db.connection import Database
from app.services.schedule_day_service import ScheduleDayService


class ScheduleService:
    def __init__(self, db: Database, day_service: ScheduleDayService):
        self.db = db
        self.day_service = day_service

    # --------------------------------------------------
    # TWORZENIE GRAFIKU
    # --------------------------------------------------
    def create_schedule(self, year: int, month: int):
        last_day = monthrange(year, month)[1]

        start_dt = datetime(year, month, 1, 0, 0, 0)
        end_dt = datetime(year, month, last_day, 23, 59, 59)

        cur = self.db.cursor(dictionary=True)

        # kolejna wersja grafiku
        cur.execute(
            "SELECT MAX(version) AS max_v FROM schedules WHERE year=%s AND month=%s",
            (year, month)
        )
        row = cur.fetchone()

        version = 1 if row["max_v"] is None else row["max_v"] + 1

        cur.execute(
            """
            INSERT INTO schedules (year, month, version, status, start_datetime, end_datetime)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (year, month, version, 'draft', start_dt, end_dt)
        )

        schedule_id = cur.lastrowid
        self.db.commit()

        # tworzenie dni grafiku
        for day_num in range(1, last_day + 1):
            day_date = date(year, month, day_num)

            if day_date.weekday() == 6:
                self.day_service.add_day(schedule_id, day_num, None, None)
            else:
                self.day_service.add_day(schedule_id, day_num, "05:00", "23:00")

        cur.close()
        print(f"Grafik {year}-{month:02d} utworzony. ID={schedule_id}")
        return schedule_id

    # --------------------------------------------------
    # LISTA GRAFIKÓW (WEBUI)
    # --------------------------------------------------
    def list_schedules(self):
        cur = self.db.cursor(dictionary=True)
        cur.execute("""
            SELECT id, year, month, version, status
            FROM schedules
            ORDER BY year DESC, month DESC, version DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows or []

    # --------------------------------------------------
    # POBRANIE JEDNEGO GRAFIKU
    # --------------------------------------------------
    def get_schedule(self, schedule_id: int):
        cur = self.db.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM schedules WHERE id=%s",
            (schedule_id,)
        )
        row = cur.fetchone()
        cur.close()
        return row

    # --------------------------------------------------
    # USUWANIE GRAFIKU
    # --------------------------------------------------
    def delete_schedule(self, schedule_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM schedule_days WHERE schedule_id=%s", (schedule_id,))
        cur.execute("DELETE FROM schedules WHERE id=%s", (schedule_id,))
        self.db.commit()
        cur.close()
        print("Grafik usunięty.")

    # --------------------------------------------------
    # LISTA DNI (WEBUI)
    # --------------------------------------------------
    def list_days(self, schedule_id: int):
        cur = self.db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s
            ORDER BY day
            """,
            (schedule_id,)
        )
        rows = cur.fetchall()
        cur.close()
        return rows or []

    # --------------------------------------------------
    # MACIERZ MIESIĄCA (WEBUI GRID)
    # --------------------------------------------------
    def get_month_matrix(self, schedule_id: int):

        cur = self.db.cursor(dictionary=True)

        # dni grafiku
        cur.execute("""
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s
            ORDER BY day
        """, (schedule_id,))
        days = cur.fetchall() or []

        # aktywni pracownicy
        cur.execute("""
            SELECT id, first_name, last_name
            FROM employees
            WHERE active=1
            ORDER BY id
        """)
        employees_raw = cur.fetchall() or []

        cur.close()

        # budujemy strukturę pod template
        employees = []

        for emp in employees_raw:

            emp_row = {
                "id": emp["id"],
                "first_name": emp["first_name"],
                "last_name": emp["last_name"],
                "days": {}
            }

            for d in days:

                if d["staff_from"] is None:
                    continue

                emp_row["days"][d["day"]] = {
                    "staff_from": str(d["staff_from"])[:5],
                    "store_close": str(d["store_close"])[:5]
                }

            employees.append(emp_row)

        return {
            "days": days,
            "employees": employees
        }
