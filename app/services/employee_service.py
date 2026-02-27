class EmployeeService:

    def __init__(self, db):
        self.db = db

    def list_employees(self, sort="last_name", order="asc"):
        allowed_fields = {
            "id": "e.id",
            "first_name": "e.first_name",
            "last_name": "e.last_name",
            "role": "r.name",
            "active": "e.active",
        }

        sort_column = allowed_fields.get(sort, "e.last_name")
        order_sql = "ASC" if order.lower() == "asc" else "DESC"

        sql = f"""
            SELECT 
                e.*,
                r.name AS role
            FROM employees e
            LEFT JOIN roles r ON e.role_id = r.id
            ORDER BY {sort_column} {order_sql}
        """

        cur = self.db.cursor()
        cur.execute(sql)
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
