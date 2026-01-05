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
        print("0. Wyjście")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            first_name = input("Imię: ").strip()
            last_name = input("Nazwisko: ").strip()
            position = input("Stanowisko: ").strip()

            print("\nDostępne role:")
            roles = service.list_roles()
            print(tabulate(roles, headers="keys", tablefmt="grid"))

            role_id = input("Wybierz ID roli: ").strip()
            role_id = int(role_id) if role_id.isdigit() else None

            service.add_employee(first_name, last_name, position, role_id)

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

        elif choice == "0":
            print("Koniec programu")
            break
        else:
            print("Nieprawidłowa opcja. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
