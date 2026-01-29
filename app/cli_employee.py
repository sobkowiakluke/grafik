# app/cli_employee.py

from app.services.employee_service import EmployeeService

def edit_employee_menu(service):
    eid = int(input("ID pracownika: "))
    employee = service.get_employee(eid)
    if not employee:
        print("Nie znaleziono pracownika.")
        return

    while True:
        print("\n=== EDYCJA PRACOWNIKA ===")
        print("1. Edytuj imię")
        print("2. Edytuj nazwisko")
        print("3. Edytuj rolę")
        print("4. Zmień status aktywny/nieaktywny")
        print("0. Powrót")

        choice = input("Wybór: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            first_name = input("Nowe imię: ")
            service.update_first_name(eid, first_name)
        elif choice == "2":
            last_name = input("Nowe nazwisko: ")
            service.update_last_name(eid, last_name)
        elif choice == "3":
            print("Dostępne role:")

            roles = service.list_roles()  # lista słowników: [{'id':1,'name':'Kasjer'}, ...]
            for r in roles:
                print(f"{r['id']}: {r['name']}")

            role_id = int(input("Wybierz ID roli: "))
            service.update_role(eid, role_id)
        elif choice == "4":
            current = employee['active']
            new_status = 0 if current else 1
            service.update_active(eid, new_status)
            print(f"Status zmieniony na: {'aktywny' if new_status else 'nieaktywny'}")
        else:
            print("Nieprawidłowa opcja.")

def main():
    service = EmployeeService()

    while True:
        print("\n=== MENU PRACOWNIKÓW ===")
        print("1. Dodaj pracownika")
        print("2. Usuń pracownika")
        print("3. Lista pracowników")
        print("4. Edytuj pracownika")
        print("0. Wyjście")

        choice = input("Wybierz opcję: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            first_name = input("Imię: ")
            last_name = input("Nazwisko: ")
            print("Dostępne role:")

            roles = service.list_roles()  # powinno zwracać listę słowników [{'id':1,'name':'Kasjer'}, ...]

            for r in roles:
                print(f"{r['id']}: {r['name']}")

            role_id = int(input("Wybierz ID roli: "))
            service.add_employee(first_name, last_name, role_id)
        elif choice == "2":
            eid = int(input("ID pracownika do usunięcia: "))
            service.delete_employee(eid)
        elif choice == "3":
            employees = service.list_employees()
            print("\n+----+------------+-----------+---------+--------+")
            print("| ID | Imię       | Nazwisko  | Rola    | Active |")
            print("+====+============+===========+=========+========+")
            for e in employees:
                role_name = service.get_role_name(e['role_id'])
                active = '✔' if e['active'] else '✘'
                print(f"| {e['id']:>2} | {e['first_name']:<10} | {e['last_name']:<9} | {role_name:<7} | {active:^6} |")
            print("+----+------------+-----------+---------+--------+")
        elif choice == "4":
            edit_employee_menu(service)
        else:
            print("Nieprawidłowa opcja.")

if __name__ == "__main__":
    main()
