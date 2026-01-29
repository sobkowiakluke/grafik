from app.db.connection import Database

class EmployeeService:






    def __init__(self):
        self.db = Database()


    def update_first_name(self, employee_id: int, first_name: str):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE employees SET first_name=%s WHERE id=%s",
            (first_name, employee_id)
        )
        self.db.commit()
        cur.close()

    def update_last_name(self, employee_id: int, last_name: str):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE employees SET last_name=%s WHERE id=%s",
            (last_name, employee_id)
        )
        self.db.commit()
        cur.close()

    def update_role(self, employee_id: int, role_id: int):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE employees SET role_id=%s WHERE id=%s",
            (role_id, employee_id)
        )
        self.db.commit()
        cur.close()

    def update_active(self, employee_id: int, active: bool):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE employees SET active=%s WHERE id=%s",
            (1 if active else 0, employee_id)
        )
        self.db.commit()
        cur.close()

    # -----------------------
    # Pracownicy
    # -----------------------
    def add_employee(self, first_name: str, last_name: str, role_id: int = None, active: int = 1):
        cur = self.db.cursor()
        query = """
        INSERT INTO employees (first_name, last_name, role_id, active)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (first_name, last_name, role_id, active))
        cur.close()
        print(f"Dodano pracownika: {first_name} {last_name} (rola id={role_id}, active={active})")


    def delete_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = "DELETE FROM employees WHERE id = %s"
        cur.execute(query, (employee_id,))
        cur.close()
        print(f"Usunięto pracownika o ID {employee_id}")

    def get_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = """
        SELECT e.id, e.first_name, e.last_name, e.active, r.name AS role
        FROM employees e
        LEFT JOIN roles r ON e.role_id = r.id
        WHERE e.id = %s
        """
        cur.execute(query, (employee_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def list_employees(self):
        cur = self.db.cursor()
        query = """
        SELECT e.id, e.first_name, e.last_name, e.role_id, e.active, r.name AS role
        FROM employees e
        LEFT JOIN roles r ON e.role_id = r.id
        ORDER BY e.id
        """
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result

    def update_employee(self, employee_id: int, first_name: str = None, last_name: str = None, role_id: int = None, active: int = None):
        cur = self.db.cursor()
        fields = []
        values = []

        if first_name:
            fields.append("first_name = %s")
            values.append(first_name)
        if last_name:
            fields.append("last_name = %s")
            values.append(last_name)
        if role_id:
            fields.append("role_id = %s")
            values.append(role_id)
        if active is not None:
            fields.append("active = %s")
            values.append(active)

        if not fields:
            print("Brak zmian do zapisania.")
            return

        values.append(employee_id)
        query = f"UPDATE employees SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, values)
        cur.close()
        print(f"Zaktualizowano pracownika o ID {employee_id}")

    # -----------------------
    # Role
    # -----------------------
    def list_roles(self):
        cur = self.db.cursor()
        query = "SELECT id, name, description FROM roles ORDER BY id"
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result

    def get_role_name(self, role_id: int) -> str:
        """Zwraca nazwę roli dla podanego role_id"""
        cur = self.db.cursor()
        cur.execute("SELECT name FROM roles WHERE id=%s", (role_id,))
        row = cur.fetchone()
        cur.close()
        return row['name'] if row else "Nieznana"
