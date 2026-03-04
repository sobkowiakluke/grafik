from flask import request
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

        cur = self.db.cursor()

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
    def list_schedules(self, sort="year", order="desc"):

        allowed_fields = {
            "id": "id",
            "year": "year",
            "month": "month",
            "version": "version",
            "status": "status",
        }

        order_sql = "ASC" if order.lower() == "asc" else "DESC"

        if sort == "year":
            # chronologiczne sortowanie: rok + miesiąc + wersja
            order_clause = f"year {order_sql}, month {order_sql}, version {order_sql}"
        else:
            sort_column = allowed_fields.get(sort, "year")
            order_clause = f"{sort_column} {order_sql}"

        sql = f"""
            SELECT id, year, month, version, status
            FROM schedules
            ORDER BY {order_clause}
        """

        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows or []


    # --------------------------------------------------
    # POBRANIE JEDNEGO GRAFIKU
    # --------------------------------------------------
    def get_schedule(self, schedule_id: int):
        cur = self.db.cursor()
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
        cur = self.db.cursor()
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

        cur = self.db.cursor()
        # pobierz rok i miesiąc grafiku
        cur.execute(
            "SELECT year, month FROM schedules WHERE id=%s",
            (schedule_id,)
        )
        schedule_row = cur.fetchone()

        year = schedule_row["year"]
        month = schedule_row["month"]
        # dni grafiku
        cur.execute("""
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s
            ORDER BY day
        """, (schedule_id,))
        days_raw = cur.fetchall() or []

        # konwersja timedelta -> HH:MM
        days = []

        for d in days_raw:

            if d["staff_from"] is None:
                days.append({
                    "day": d["day"],
                    "staff_from": None,
                    "store_close": None
                })
                continue

            def td_to_hhmm(td):
                total = int(td.total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                return f"{h:02d}:{m:02d}"

            days.append({
                "day": d["day"],
                "staff_from": td_to_hhmm(d["staff_from"]),
                "store_close": td_to_hhmm(d["store_close"])
            })

        # aktywni pracownicy
        cur.execute("""
            SELECT id, first_name, last_name
            FROM employees
            WHERE active=1
            ORDER BY id
        """)
        employees_raw = cur.fetchall() or []



        # zakres miesiąca
        from datetime import date
        from calendar import monthrange

        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        # pobierz wolne w tym miesiącu
        cur.execute("""
            SELECT employee_id, date_from, date_to
            FROM employee_time_off
            WHERE NOT (
                date_to < %s OR date_from > %s
            )
        """, (start_date, end_date))

        time_off_rows = cur.fetchall() or []


        # =====================================
        # SHIFTS (WORK)
        # =====================================
        cur.execute("""
            SELECT employee_id, DAY(shift_date) AS day
            FROM shifts
            WHERE schedule_id = %s
        """, (schedule_id,))

        shift_rows = cur.fetchall()

        for row in shift_rows:
            emp_id = row["employee_id"]
        day = row["day"]


        # budujemy mapę
        time_off_map = {}

        for row in time_off_rows:
            emp_id = row["employee_id"]
            start = row["date_from"]
            end = row["date_to"]

            if emp_id not in time_off_map:
                time_off_map[emp_id] = []

            time_off_map[emp_id].append((start, end))

                # budujemy strukturę pod template
        employees = []


        cur.execute("""
            SELECT employee_id, shift_date
            FROM shifts
            WHERE schedule_id = %s
        """, (schedule_id,))

        shift_rows = cur.fetchall()

        shift_set = set(
            (row["employee_id"], row["shift_date"])
            for row in shift_rows
        )


        # budujemy strukturę pod template
        employees = []


        cur.execute("""
            SELECT employee_id, shift_date
            FROM shifts
            WHERE schedule_id = %s
        """, (schedule_id,))

        shift_rows = cur.fetchall()

        shift_set = set(
            (row["employee_id"], row["shift_date"])
            for row in shift_rows
        )


        for emp in employees_raw:

            emp_row = {
                "id": emp["id"],
                "first_name": emp["first_name"],
                "last_name": emp["last_name"],
                "days": {}
            }

            for d in days:

                day_number = d["day"]
                current_date = date(year, month, day_number)

                is_time_off = False
                is_work = False

                if (emp["id"], current_date) in shift_set:
                    is_work = True

                if emp["id"] in time_off_map:
                    for start, end in time_off_map[emp["id"]]:
                        if start <= current_date <= end:
                            is_time_off = True
                            is_work = False
                            break

                if d["staff_from"] is None:
                    emp_row["days"][day_number] = {
                        "staff_from": None,
                        "store_close": None,
                        "is_time_off": is_time_off,
                        "is_work": is_work
                   }
                    continue

                emp_row["days"][day_number] = {
                    "staff_from": str(d["staff_from"])[:5],
                    "store_close": str(d["store_close"])[:5],
                    "is_time_off": is_time_off,
                    "is_work": is_work
                }

            employees.append(emp_row)
            cur.close()
        return {
            "days": days,
            "employees": employees
        }

    from app import db
    from app.services.schedule_day_service import ScheduleDayService


    def update_day_hours(self, schedule_id, day, staff_from, store_close):

        day_service = ScheduleDayService(self.db)

        day_service.set_day_hours(
            schedule_id,
            day,
            staff_from,
            store_close
        )


    def edit_shift(self, shift_id, start, end):

        cur = self.db.cursor()

        cur.execute("""
            UPDATE shifts
            SET start_time=%s,
                end_time=%s
            WHERE id=%s
        """, (start, end, shift_id))

        self.db.commit()
        cur.close()
