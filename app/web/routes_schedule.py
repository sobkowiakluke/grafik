from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from app.db.connection import Database
from app.services.schedule_service import ScheduleService
from app.services.schedule_day_service import ScheduleDayService


# =====================================================
# Blueprint
# =====================================================
schedule_bp = Blueprint("schedule_bp", __name__)


# =====================================================
# Dependency Injection (tak jak w Twoim CLI)
# =====================================================
db = Database()
day_service = ScheduleDayService(db)
schedule_service = ScheduleService(db, day_service)


# =====================================================
# Lista grafików
# URL finalny: /schedules/list
# =====================================================
@schedule_bp.route("/list")
@login_required
def list_schedules():
    schedules = schedule_service.list_schedules()
    return render_template(
        "schedule_list.html",
        schedules=schedules
    )


# =====================================================
# Szczegóły grafiku
# URL: /schedules/<id>
# =====================================================
@schedule_bp.route("/<int:schedule_id>")
@login_required
def schedule_details(schedule_id):

    schedule = schedule_service.get_schedule(schedule_id)
    matrix = schedule_service.get_month_matrix(schedule_id)

    return render_template(
        "schedule_month.html",
        schedule=schedule,
        matrix=matrix
    )
# =====================================================
# Widok miesiąca (macierz)
# URL: /schedules/<id>/month
# =====================================================
@schedule_bp.route("/<int:schedule_id>/month")
@login_required
def schedule_month(schedule_id):
    schedule, matrix = schedule_service.get_schedule_month_matrix(schedule_id)
    return render_template(
        "schedule_month.html",
        schedule=schedule,
        matrix=matrix
    )


# =====================================================
# Dodawanie grafiku z WebUI
# URL: /schedules/add
# =====================================================
@schedule_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_schedule():

    if request.method == "POST":
        year = int(request.form["year"])
        month = int(request.form["month"])

        # ta sama logika co CLI
        schedule_service.create_schedule(year, month)

        # wracamy do listy grafików
        return redirect(url_for("schedule_bp.list_schedules"))

    return render_template("schedule_add.html")
