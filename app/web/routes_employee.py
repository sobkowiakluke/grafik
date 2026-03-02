from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.db.provider import get_db
from app.services.employee_service import EmployeeService


employee_bp = Blueprint("employee", __name__, template_folder="templates")



@employee_bp.route(
    "/employees/<int:employee_id>/time-off/<date_str>",
    methods=["GET", "POST"]
)
@login_required
def edit_time_off(employee_id, date_str):

    from datetime import datetime
    db = get_db()
    cur = db.cursor()

    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # znajdź wpis obejmujący ten dzień
    cur.execute("""
        SELECT *
        FROM employee_time_off
        WHERE employee_id = %s
          AND %s BETWEEN date_from AND date_to
        LIMIT 1
    """, (employee_id, selected_date))

    row = cur.fetchone()

    if not row:
        cur.close()
        flash("Brak wpisu wolnego dla tej daty.", "danger")
        return redirect(request.referrer or url_for("schedule_bp.list_schedules"))




    if request.method == "POST":

        reason_id = request.form.get("reason_id")

        if not reason_id:
            flash("Wybierz przyczynę.", "danger")
            return redirect(request.url)

        date_from = request.form.get("date_from")
        date_to = request.form.get("date_to")
        notes = request.form.get("notes")

        cur.execute("""
             UPDATE employee_time_off
             SET date_from=%s,
                 date_to=%s,
                 notes=%s,
                 reason_id=%s
             WHERE id=%s
        """, (date_from, date_to, notes, reason_id, row["id"]))

        db.commit()
        cur.close()

        flash("Wolne zaktualizowane.", "success")

        back = request.form.get("back")

        return redirect(
            back or url_for("schedule_bp.schedule_details",
                            schedule_id=request.args.get("schedule_id"))
        )

    cur.close()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM time_off_reasons ORDER BY name")
    reasons = cur.fetchall()
    cur.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template(
            "time_off_form_partial.html",
            time_off=row,
            employee_id=employee_id,
            selected_date=selected_date,
            reasons=reasons,
        )
    return render_template(
        "time_off_form.html",
        time_off=row,
        employee_id=employee_id,
        selected_date=selected_date,
        reasons=reasons,
        back=request.args.get("back")
    )

def get_employee_service():
    return EmployeeService(get_db())

@employee_bp.route("/list")
@login_required
def list_employees():
    service = get_employee_service()

    sort = request.args.get("sort", "last_name")
    order = request.args.get("order", "asc")

    employees = service.list_employees(sort=sort, order=order)

    next_order = "desc" if order == "asc" else "asc"

    return render_template(
        "employee_list.html",
        employees=employees,
        current_sort=sort,
        current_order=order,
        next_order=next_order,
    )

@employee_bp.route("/add", methods=["GET"])
@login_required
def add_employee_form():
    service = get_employee_service()
    roles = service.list_roles()
    return render_template("employee_add.html", roles=roles)


@employee_bp.route("/add", methods=["POST"])
@login_required
def add_employee():
    service = get_employee_service()

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    role_id = request.form.get("role_id")
    active = 1 if request.form.get("active") else 0

    service.add_employee(first_name, last_name, role_id, active)

    return redirect(url_for("employee.list_employees"))


@employee_bp.route("/employees/edit/<int:employee_id>", methods=["POST"])
@login_required
def edit_employee(employee_id):

    service = get_employee_service()

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    role_id = request.form.get("role_id") or None
    active = request.form.get("active")
    active_flag = 1 if active == "on" else 0

    service.update_employee(
        employee_id,
        first_name,
        last_name,
        role_id,
        active_flag,
    )

    flash(f"Pracownik {first_name} {last_name} zaktualizowany.", "success")

    return redirect(url_for("employee.list_employees"))


@employee_bp.route("/employees/delete/<int:employee_id>", methods=["POST"])
@login_required
def delete_employee(employee_id):

    service = get_employee_service()
    service.delete_employee(employee_id)

    flash(f"Pracownik o ID {employee_id} usunięty.", "warning")

    return redirect(url_for("employee.list_employees"))



@employee_bp.route("/time-off/add", methods=["GET", "POST"])
@login_required
def add_time_off():

    from app.db.provider import get_db
    from flask import request, redirect, url_for

    db = get_db()
    cur = db.cursor()

    # GET – tylko render formularza
    if request.method == "GET":

        cur.execute("""
            SELECT id, first_name, last_name
            FROM employees
            WHERE active = 1
            ORDER BY last_name, first_name
        """)
        employees = cur.fetchall()

        cur.execute("""
            SELECT id, name
            FROM time_off_reasons
            WHERE active = TRUE
            ORDER BY name
        """)
        reasons = cur.fetchall()

        cur.close()

        return render_template(
            "employee_time_off_form.html",
            employees=employees,
            reasons=reasons
        )

    # POST
    employee_id = request.form.get("employee_id")
    date_from = request.form.get("date_from")
    date_to = request.form.get("date_to")
    reason_id = request.form.get("reason_id")
    notes = request.form.get("notes")

    # walidacja podstawowa
    if not employee_id or not date_from or not date_to or not reason_id:
        return "Brak wymaganych danych", 400

    if date_from > date_to:
        return "Data początkowa nie może być późniejsza niż końcowa", 400

    # 🔎 sprawdzenie kolizji
    cur.execute("""
        SELECT id
        FROM employee_time_off
        WHERE employee_id = %s
        AND NOT (
            date_to < %s OR date_from > %s
        )
    """, (employee_id, date_from, date_to))

    collision = cur.fetchone()

    if collision:
        cur.close()
        return "Ten pracownik ma już wolne w podanym zakresie", 400

    # ✅ INSERT
    cur.execute("""
        INSERT INTO employee_time_off
        (employee_id, date_from, date_to, reason_id, notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (employee_id, date_from, date_to, reason_id, notes))

    db.commit()
    cur.close()

    return "Zapisano poprawnie"


