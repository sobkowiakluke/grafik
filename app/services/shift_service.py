def is_employee_available(db, employee_id, shift_date, start_time, end_time):
    cur = db.cursor()

    # 1️⃣ Time off (zakres date_from → date_to)
    cur.execute("""
        SELECT id
        FROM employee_time_off
        WHERE employee_id = %s
          AND %s BETWEEN date_from AND date_to
        LIMIT 1
    """, (employee_id, shift_date))

    if cur.fetchone():
        cur.close()
        return False, "Employee has time off on this day"

    # 2️⃣ Overlapping shift
    cur.execute("""
        SELECT id
        FROM shifts
        WHERE employee_id = %s
          AND shift_date = %s
          AND (%s < end_time AND %s > start_time)
        LIMIT 1
    """, (employee_id, shift_date, start_time, end_time))

    if cur.fetchone():
        cur.close()
        return False, "Shift overlaps with existing shift"

    cur.close()
    return True, None

def delete_shift(self, shift_id):

    cur = self.db.cursor()

    cur.execute("""
        DELETE FROM shifts
        WHERE id = %s
    """, (shift_id,))

    self.db.commit()
    cur.close()
