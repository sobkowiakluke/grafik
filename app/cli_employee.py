from app.services.employee_service import EmployeeService
from tabulate import tabulate

def main():
    service = EmployeeService()

    while True:
        print("\n=== MENU PRACOWNIKÓW ===")
        print("1. Dodaj pracownika")
        print("2. Usuń pracownika")
        print("3. Lista wszystkich pracowników")
        print("4. Pokaż pracownika po ID")
        print("5. Lista ról")
        print("6. Edytuj pracownika")
        print("0. Wyjście")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            first_name = input("Imię: ").strip()
            last_name = input("Nazwisko: ").strip()

            # wybór aktywności
            active_input = input("Czy pracownik aktywny? (1 = tak, 0 = nie, domyślnie 1): ").strip()
            active = int(active_input) if active_input in ("0", "1") else 1

            # wybór roli
            print("\nDostępne role:")
            roles = service.list_roles()
            print(tabulate(roles, headers="keys", tablefmt="grid"))
            role_input = input("Wybierz ID roli: ").strip()
            role_id = int(role_input) if role_input.isdigit() else None

            service.add_employee(first_name, last_name, role_id, active)

        elif choice == "2":
            emp_id = input("ID pracownika do usunięcia: ").strip()
            service.delete_employee(int(emp_id))

        elif choice == "3":
            employees = service.list_employees()
            if employees:
                print("\nLista pracowników:")
                print(tabulate(employees, headers="keys", tablefmt="grid"))
            else:
                print("Brak pracowników w systemie.")

        elif choice == "4":
            emp_id = input("ID pracownika: ").strip()
            emp = service.get_employee(int(emp_id))
            if emp:
                print(tabulate([emp], headers="keys", tablefmt="grid"))
            else:
                print(f"Nie znaleziono pracownika o ID {emp_id}")

        elif choice == "5":
            roles = service.list_roles()
            if roles:
                print("\nDostępne role:")
                print(tabulate(roles, headers="keys", tablefmt="grid"))
            else:
                print("Brak ról w systemie.")

        elif choice == "6":
            emp_id = input("ID pracownika do edycji: ").strip()
            emp_id = int(emp_id)

            first_name = input("Nowe imię (Enter = bez zmiany): ").strip()
            last_name = input("Nowe nazwisko (Enter = bez zmiany): ").strip()

            print("\nDostępne role:")
            roles = service.list_roles()
            print(tabulate(roles, headers="keys", tablefmt="grid"))
            role_input = input("ID nowej roli (Enter = bez zmiany): ").strip()
            role_id = int(role_input) if role_input.isdigit() else None

            active_input = input("Czy pracownik aktywny? (1 = tak, 0 = nie, Enter = bez zmiany): ").strip()
            active = int(active_input) if active_input in ("0", "1") else None

            service.update_employee(emp_id,
                                    first_name=first_name if first_name else None,
                                    last_name=last_name if last_name else None,
                                    role_id=role_id,
                                    active=active)

        elif choice == "0":
            print("Koniec programu")
            break

        else:
            print("Nieprawidłowa opcja. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
