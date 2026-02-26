class EmployeeService:

    def __init__(self, db):
        self.db = db

    def list_employees(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM employees ORDER BY last_name")
        rows = cur.fetchall()
        cur.close()
        return rows

    def list_roles(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM roles ORDER BY name")
        rows = cur.fetchall()
        cur.close()
        return rows

    def add_employee(self, first_name, last_name, role_id, active):
        cur = self.db.cursor()
        cur.execute(
            """
            INSERT INTO employees (first_name, last_name, role_id, active)
            VALUES (%s,%s,%s,%s)
            """,
            (first_name, last_name, role_id, active),
        )
        self.db.commit()
        cur.close()

    def update_employee(self, employee_id, first_name, last_name, role_id, active):
        cur = self.db.cursor()
        cur.execute(
            """
            UPDATE employees
            SET first_name=%s,
                last_name=%s,
                role_id=%s,
                active=%s
            WHERE id=%s
            """,
            (first_name, last_name, role_id, active, employee_id),
        )
        self.db.commit()
        cur.close()

    def delete_employee(self, employee_id):
        cur = self.db.cursor()
        cur.execute("DELETE FROM employees WHERE id=%s", (employee_id,))
        self.db.commit()
        cur.close()
