from app.db.connection import Database
from app.services.schedule_service import ScheduleService
from app.services.schedule_day_service import ScheduleDayService

# Inicjalizacja bazy
db = Database()  # użyj już gotowego singletona lub parametrów z config
day_service = ScheduleDayService(db)
schedule_service = ScheduleService(db, day_service)

def main():
    while True:
        print("\n=== MENU GRAFIKÓW ===")
        print("1. Utwórz grafik")
        print("2. Usuń grafik")
        print("3. Lista grafików")
        print("4. Pokaż grafik po ID")
        print("5. Edytuj grafik")
        print("0. Wyjście")

        choice = input("Wybierz opcję: ")

        if choice == "0":
            break

        elif choice == "1":
            year = int(input("Rok: "))
            month = int(input("Miesiąc (1-12): "))
            schedule_service.create_schedule(year, month)

        elif choice == "2":
            sid = int(input("ID grafiku do usunięcia: "))
            schedule_service.delete_schedule(sid)

        elif choice == "3":
            schedules = schedule_service.list_schedules()
            print("\n+------+--------+---------+-----------+----------+---------------------+---------------------+")
            print("|   id |   year |   month | version   | status   | start_datetime      | end_datetime        |")
            print("+------+--------+---------+-----------+----------+---------------------+---------------------+")
            for s in schedules:
                print(f"| {s['id']:>3} | {s['year']:>6} | {s['month']:>7} | {s['version']:>9} | {s['status']:<8} | "
                      f"{s['start_datetime']} | {s['end_datetime']} |")
            print("+------+--------+---------+-----------+----------+---------------------+---------------------+")

        elif choice == "4":
            sid = int(input("ID grafiku: "))
            sched = schedule_service.get_schedule(sid)
            if sched:
                print(sched)
                day_service.list_days(sid)
            else:
                print("Nie znaleziono grafiku.")

        elif choice == "5":
            sid = int(input("ID grafiku do edycji: "))
            edit_schedule_menu(sid)


def edit_schedule_menu(schedule_id):
    while True:
        print("\n=== EDYCJA GRAFIKU ===")
        print("1. Pokaż dni grafiku")
        print("2. Ustaw godziny dnia")
        print("3. Usuń godziny (dzień wolny)")
        print("0. Powrót")

        choice = input("Wybór: ")

        if choice == "0":
            break
        elif choice == "1":
            day_service.list_days(schedule_id)
        elif choice == "2":
            day_number = int(input("Dzień miesiąca: "))
            staff_from = input("Załoga od (HH:MM): ")
            store_close = input("Zamknięcie sklepu (HH:MM): ")
            day_service.set_day_hours(day_number, schedule_id, staff_from, store_close)
            print("Godziny dnia zapisane")
        elif choice == "3":
            day_number = int(input("Dzień miesiąca: "))
            day_service.clear_day_hours(schedule_id, day_number)
            print("Dzień ustawiony jako wolny")


if __name__ == "__main__":
    main()
