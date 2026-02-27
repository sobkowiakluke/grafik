from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.db.provider import get_db
from app.services.employee_service import EmployeeService


employee_bp = Blueprint("employee", __name__, template_folder="templates")


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
