from app.services.employee_service import EmployeeService

def main():
    service = EmployeeService()

    # Lista dostępnych ról
    print("Role w systemie:")
    for role in service.list_roles():
        print(role)

    # Dodajemy pracowników z rolami
    service.add_employee("Jan", "Kowalski", "Kasjer", role_id=1)
    service.add_employee("Anna", "Nowak", "Starszy kasjer", role_id=2)

    # Lista wszystkich
    print("\nLista pracowników:")
    for emp in service.list_employees():
        print(emp)

    # Pobranie pracownika po ID
    print("\nPracownik o ID 1:")
    print(service.get_employee(1))

    # Usuwanie
    service.delete_employee(1)

if __name__ == "__main__":
    main()
