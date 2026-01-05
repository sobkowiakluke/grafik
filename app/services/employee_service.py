from app.db.connection import Database

class EmployeeService:
    def __init__(self):
        self.db = Database()

    def add_employee(self, first_name: str, last_name: str, position: str):
        cur = self.db.cursor()
        query = "INSERT INTO employees (first_name, last_name, position) VALUES (%s, %s, %s)"
        cur.execute(query, (first_name, last_name, position))
        cur.close()
        print(f"Dodano pracownika: {first_name} {last_name}")

    def delete_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = "DELETE FROM employees WHERE id = %s"
        cur.execute(query, (employee_id,))
        cur.close()
        print(f"Usunięto pracownika o ID {employee_id}")

    def get_employee(self, employee_id: int):
        cur = self.db.cursor()
        query = "SELECT * FROM employees WHERE id = %s"
        cur.execute(query, (employee_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def list_employees(self):
        cur = self.db.cursor()
        query = "SELECT * FROM employees ORDER BY id"
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result
