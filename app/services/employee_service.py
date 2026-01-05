from app.db.connection import Database

class EmployeeService:
    def __init__(self):
        self.db = Database()

    # -----------------------
    # Pracownicy
    # -----------------------
    def add_employee(self, first_name: str, last_name: str, position: str, role_id: int = None):
        cur = self.db.cursor()
        query = """
        INSERT INTO employees (first_name, last_name, position, role_id)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (first_name, last_name, position, role_id))
        cur.close()
        print(f"Dodano pracownika: {first_name} {last_name} (rola id={role_id})")

    def delete_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = "DELETE FROM employees WHERE id = %s"
        cur.execute(query, (employee_id,))
        cur.close()
        print(f"Usunięto pracownika o ID {employee_id}")

    def get_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = """
        SELECT e.id, e.first_name, e.last_name, e.position, r.name AS role
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
        SELECT e.id, e.first_name, e.last_name, e.position, r.name AS role
        FROM employees e
        LEFT JOIN roles r ON e.role_id = r.id
        ORDER BY e.id
        """
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result

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
