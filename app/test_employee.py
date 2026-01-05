from app.services.employee_service import EmployeeService

def main():
    service = EmployeeService()

    # Dodajemy pracowników
    service.add_employee("Jan", "Kowalski", "Kasjer")
    service.add_employee("Anna", "Nowak", "Magazynier")

    # Lista wszystkich
    print("Lista pracowników:")
    for emp in service.list_employees():
        print(emp)

    # Pobranie pracownika po ID
    print("Pracownik o ID 1:")
    print(service.get_employee(1))

    # Usuwanie
    service.delete_employee(1)

if __name__ == "__main__":
    main()
