from app.db.connection import Database

class ScheduleDayService:
    """
    Zarządza dniami grafiku (tabela schedule_days):

    - tworzenie dni przy nowym grafiku
    - ustawianie godzin pracy
    - oznaczanie dnia jako wolny
    - listowanie dni grafiku (dla WebUI)
    """

    def __init__(self, db: Database):
        self.db = db

    # -------------------------------------------------
    # Tworzenie dnia
    # -------------------------------------------------
    def add_day(
        self,
        schedule_id: int,
        day_number: int,
        staff_from: str | None = None,
        store_close: str | None = None,
    ):
        """
        Dodaje rekord dnia.
        Jeśli staff_from/store_close = None → dzień wolny.
        """
        cur = self.db.cursor()
        cur.execute(
            """
            INSERT INTO schedule_days (schedule_id, day, staff_from, store_close)
            VALUES (%s, %s, %s, %s)
            """,
            (schedule_id, day_number, staff_from, store_close),
        )
        self.db.commit()
        cur.close()

    # -------------------------------------------------
    # Ustawienie godzin dnia
    # -------------------------------------------------
    def set_day_hours(
        self,
        schedule_id: int,
        day_number: int,
        staff_from: str,
        store_close: str,
    ):
        cur = self.db.cursor()
        cur.execute(
            """
            UPDATE schedule_days
            SET staff_from=%s, store_close=%s
            WHERE schedule_id=%s AND day=%s
            """,
            (staff_from, store_close, schedule_id, day_number),
        )
        self.db.commit()
        cur.close()

    # -------------------------------------------------
    # Ustawienie dnia wolnego
    # -------------------------------------------------
    def clear_day_hours(self, schedule_id: int, day_number: int):
        cur = self.db.cursor()
        cur.execute(
            """
            UPDATE schedule_days
            SET staff_from=NULL, store_close=NULL
            WHERE schedule_id=%s AND day=%s
            """,
            (schedule_id, day_number),
        )
        self.db.commit()
        cur.close()

    # -------------------------------------------------
    # Lista dni grafiku (WEB)
    # -------------------------------------------------
    def list_days(self, schedule_id: int):
        """
        Zwraca listę dni grafiku:
        [
            {day: 1, staff_from: time, store_close: time},
            ...
        ]
        """
        cur = self.db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s
            ORDER BY day
            """,
            (schedule_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return rows or []

    # -------------------------------------------------
    # Jeden dzień
    # -------------------------------------------------
    def get_day(self, schedule_id: int, day_number: int):
        cur = self.db.cursor(dictionary=True)
        cur.execute(
            """
            SELECT day, staff_from, store_close
            FROM schedule_days
            WHERE schedule_id=%s AND day=%s
            """,
            (schedule_id, day_number),
        )
        row = cur.fetchone()
        cur.close()
        return row

    from app import db

    def update_hours(self, schedule_id, day, staff_from, store_close):

        row = ScheduleDay.query.filter_by(
            schedule_id=schedule_id,
            day=day
        ).first()

        if not row:
            return

        row.staff_from = staff_from
        row.store_close = store_close

        db.session.commit()

    def update_hours(self, schedule_id, day, staff_from, store_close):

        sql = """
            UPDATE schedule_days
            SET staff_from = %s,
                store_close = %s
            WHERE schedule_id = %s
              AND day = %s
        """

        conn = self.db.connection
        cur = conn.cursor()

        cur.execute(sql, (
            staff_from,
            store_close,
            schedule_id,
            day
        ))

        conn.commit()
        cur.close()
