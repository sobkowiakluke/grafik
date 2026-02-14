from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.employee_service import EmployeeService
from flask_login import login_required

employee_bp = Blueprint('employee', __name__, template_folder='templates')
employee_service = EmployeeService()

@employee_bp.route('/list')
@login_required
def list_employees():
    employees = employee_service.list_employees()
    return render_template("employee_list.html", employees=employees)

@employee_bp.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    role_id = request.form.get('role_id') or None
    employee_service.add_employee(first_name, last_name, role_id)
    flash(f"Pracownik {first_name} {last_name} dodany.", "success")
    return redirect(url_for('employee_bp.list_employees'))

@employee_bp.route('/employees/edit/<int:employee_id>', methods=['POST'])
@login_required
def edit_employee(employee_id):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    role_id = request.form.get('role_id') or None
    active = request.form.get('active')
    active_flag = 1 if active == 'on' else 0
    employee_service.update_employee(employee_id, first_name, last_name, role_id, active_flag)
    flash(f"Pracownik {first_name} {last_name} zaktualizowany.", "success")
    return redirect(url_for('employee_bp.list_employees'))

@employee_bp.route('/employees/delete/<int:employee_id>', methods=['POST'])
@login_required
def delete_employee(employee_id):
    employee_service.delete_employee(employee_id)
    flash(f"Pracownik o ID {employee_id} usunięty.", "warning")
    return redirect(url_for('employee_bp.list_employees'))
