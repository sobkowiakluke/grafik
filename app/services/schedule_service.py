
from calendar import monthrange
from datetime import datetime, date

from app.db.connection import Database
from app.services.schedule_day_service import ScheduleDayService


class ScheduleService:

    def delete_shift(self, shift_id):

        cur = self.db.cursor()

        cur.execute(
            "DELETE FROM shifts WHERE id = %s",
            (shift_id,)
        )
        self.db.commit()
        cur.close()


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

        cur.execute(
            "SELECT MAX(version) AS max_v FROM schedules WHERE year=%s AND month=%s",
            (year, month)
        )
        row = cur.fetchone()

        version = 1 if row["max_v"] is None else row["max_v"] + 1

        cur.execute("""
            INSERT INTO schedules (year, month, version, status, start_datetime, end_datetime)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (year, month, version, "draft", start_dt, end_dt))

        schedule_id = cur.lastrowid
        self.db.commit()

        for day_num in range(1, last_day + 1):

            day_date = date(year, month, day_num)

            if day_date.weekday() == 6:
                self.day_service.add_day(schedule_id, day_num, None, None)
            else:
                self.day_service.add_day(schedule_id, day_num, "05:00", "23:00")

        cur.close()
        return schedule_id

    # --------------------------------------------------
    # LISTA GRAFIKÓW
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
    # POBRANIE GRAFIKU
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
    # LISTA DNI
    # --------------------------------------------------
    def list_days(self, schedule_id: int):

        cur = self.db.cursor()

        cur.execute("""
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s
            ORDER BY day
        """, (schedule_id,))

        rows = cur.fetchall()
        cur.close()

        return rows or []

    # --------------------------------------------------
    # MACIERZ GRAFIKU (GRID)
    # --------------------------------------------------
    def get_month_matrix(self, schedule_id: int):

        cur = self.db.cursor()

        # rok i miesiąc
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

        def td_to_hhmm(td):

            if td is None:
                return None

            total = int(td.total_seconds())
            h = total // 3600
            m = (total % 3600) // 60

            return f"{h:02d}:{m:02d}"

        days = []

        for d in days_raw:

            if d["staff_from"] is None:

                days.append({
                    "day": d["day"],
                    "staff_from": None,
                    "store_close": None
                })

                continue

            days.append({
                "day": d["day"],
                "staff_from": td_to_hhmm(d["staff_from"]),
                "store_close": td_to_hhmm(d["store_close"])
            })

        # pracownicy
        cur.execute("""
            SELECT id, first_name, last_name
            FROM employees
            WHERE active=1
            ORDER BY id
        """)

        employees_raw = cur.fetchall() or []

        # wolne
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])

        cur.execute("""
            SELECT employee_id, date_from, date_to
            FROM employee_time_off
            WHERE NOT (date_to < %s OR date_from > %s)
        """, (start_date, end_date))

        time_off_rows = cur.fetchall() or []

        time_off_map = {}

        for row in time_off_rows:

            emp_id = row["employee_id"]

            if emp_id not in time_off_map:
                time_off_map[emp_id] = []

            time_off_map[emp_id].append(
                (row["date_from"], row["date_to"])
            )

        # zmiany
        cur.execute("""
            SELECT employee_id, shift_date, start_time, end_time
            FROM shifts
            WHERE schedule_id=%s
        """, (schedule_id,))

        shift_rows = cur.fetchall() or []

        shift_map = {
            (row["employee_id"], row["shift_date"]): row
            for row in shift_rows
        }

        employees = []

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

                if emp["id"] in time_off_map:

                    for start, end in time_off_map[emp["id"]]:

                        if start <= current_date <= end:
                            is_time_off = True
                            break

                shift = shift_map.get((emp["id"], current_date))
                is_work = shift is not None

                if is_time_off:
                    is_work = False

                cell = {
                    "staff_from": d["staff_from"],
                    "store_close": d["store_close"],
                    "is_time_off": is_time_off,
                    "is_work": is_work
                }

                if shift:

                    cell["start"] = shift["start_time"]
                    cell["end"] = shift["end_time"]

                emp_row["days"][day_number] = cell

            employees.append(emp_row)

        cur.close()

        return {
            "days": days,
            "employees": employees
        }

    # --------------------------------------------------
    # EDYCJA GODZIN DNIA
    # --------------------------------------------------
    def update_day_hours(self, schedule_id, day, staff_from, store_close):

        day_service = ScheduleDayService(self.db)

        day_service.set_day_hours(
            schedule_id,
            day,
            staff_from,
            store_close
        )

    # --------------------------------------------------
    # EDYCJA ZMIANY
    # --------------------------------------------------
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

    def get_employee_hours(self, schedule_id):
        cur = self.db.cursor()
        cur.execute("""
            SELECT
                employee_id,
                SUM(TIMESTAMPDIFF(MINUTE, start_time, end_time)) AS minutes
            FROM shifts
            WHERE schedule_id = %s
            GROUP BY employee_id
        """, (schedule_id,))
        rows = cur.fetchall()
        cur.close()

        result = {}

        for r in rows:
            total_minutes = r["minutes"] or 0
            hours = int(total_minutes // 60)
            minutes = int(total_minutes % 60)
            result[r["employee_id"]] = f"{hours}:{minutes:02d}"

        return result
