from app.services.schedule_service import ScheduleService
from tabulate import tabulate

def main():
    service = ScheduleService()

    while True:
        print("\n=== MENU GRAFIKÓW ===")
        print("1. Utwórz grafik (miesiąc)")
        print("2. Usuń grafik")
        print("3. Lista grafików")
        print("4. Pokaż grafik po ID")
        print("5. Edytuj grafik (status)")
        print("0. Powrót")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            year = int(input("Rok (np. 2026): "))
            month = int(input("Miesiąc (1-12): "))
            service.create_schedule(year, month)

        elif choice == "2":
            sid = int(input("ID grafiku do usunięcia: "))
            service.delete_schedule(sid)

        elif choice == "3":
            schedules = service.list_schedules()
            if schedules:
                print(tabulate(schedules, headers="keys", tablefmt="grid"))
            else:
                print("Brak grafików.")

        elif choice == "4":
            sid = int(input("ID grafiku: "))
            sched = service.get_schedule(sid)
            if sched:
                print(tabulate([sched], headers="keys", tablefmt="grid"))
            else:
                print("Nie znaleziono grafiku.")

        elif choice == "5":
            sid = int(input("ID grafiku: "))
            print("Dostępne statusy: draft / approved / archived")
            status = input("Nowy status: ").strip()
            service.update_status(sid, status)  # serwis wykona walidację
        elif choice == "0":
            break
        else:
            print("Nieprawidłowa opcja.")

if __name__ == "__main__":
    main()
