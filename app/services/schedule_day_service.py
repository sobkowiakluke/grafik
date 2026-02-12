from datetime import datetime
from app.db.connection import Database

class ScheduleDayService:
    """
    Zarządza pojedynczymi dniami w grafiku:
    - tworzenie dni przy nowym grafiku
    - ustawianie godzin pracy
    - oznaczanie dnia jako wolny
    - listowanie dni grafiku
    """

    def __init__(self, db: Database):
        self.db = db

    def add_day(self, schedule_id: int, day_number: int):
        """
        Dodaje nowy rekord dnia do tabeli schedule_days dla danego grafiku.
        day_number: liczba dnia miesiąca (1..31)
        """
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO schedule_days (schedule_id, day) VALUES (%s, %s)",
            (schedule_id, day_number)
        )
        self.db.commit()  # <- tutaj
        cur.close()

    def set_day_hours(self, day_number: int, schedule_id: int, staff_from: str, store_close: str):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE schedule_days "
            "SET staff_from=%s, store_close=%s "
            "WHERE schedule_id=%s AND day=%s",
            (staff_from, store_close, schedule_id, day_number)
        )
        self.db.commit()
        cur.close()
        print(f"Dzień {day_number} zaktualizowany: {staff_from} → {store_close}")

    def clear_day_hours(self, day_number: int, schedule_id: int):
        """
        Oznacza dany dzień jako wolny, czyli usuwa godziny pracy.
        """
        cur = self.db.cursor()
        cur.execute(
            "UPDATE schedule_days "
            "SET staff_from=NULL, store_close=NULL "
            "WHERE schedule_id=%s AND day=%s",
            (schedule_id, day_number)
        )
        self.db.commit()
        cur.close()
        print(f"Dzień {day_number} ustawiony jako wolny")

    def list_days(self, schedule_id: int):
        """
        Wyświetla wszystkie dni grafiku w formie tabeli.
        Pokazuje dzień miesiąca i godziny pracy lub 'WOLNE' jeśli brak godzin.
        """
        cur = self.db.cursor(dictionary=True)
        cur.execute(
            "SELECT day, staff_from, store_close "
            "FROM schedule_days "
            "WHERE schedule_id=%s ORDER BY day",
            (schedule_id,)
        )
        rows = cur.fetchall()
        cur.close()

        print("\n+----+----------+----------+")
        print("| Dzień | Od       | Do       |")
        print("+====+==========+==========+")

        for r in rows:
            if r["staff_from"] is None:
                print(f"| {r['day']:>4} | WOLNE   | WOLNE   |")
            else:
                # r['staff_from'] i r['store_close'] są timedelta, konwertujemy
                staff_from_td = r["staff_from"]
                store_close_td = r["store_close"]

                # funkcja pomocnicza konwertująca timedelta -> HH:MM
                def td_to_hhmm(td):
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    return f"{hours:02d}:{minutes:02d}"

                staff_from_str = td_to_hhmm(staff_from_td)
                store_close_str = td_to_hhmm(store_close_td)

                print(f"| {r['day']:>4} | {staff_from_str:<8} | {store_close_str:<8} |")

        print("+----+----------+----------+")
