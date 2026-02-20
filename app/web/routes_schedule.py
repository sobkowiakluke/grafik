from flask import render_template, request, redirect, url_for
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
@schedule_bp.route("/<int:schedule_id>", methods=["GET", "POST"])
@login_required
def schedule_details(schedule_id):

    # =====================================
    # PARAMETRY
    # =====================================
    edit_day = request.args.get("edit_day", type=int)

    # =====================================
    # ZAPIS GODZIN (POST)
    # =====================================
    if request.method == "POST" and edit_day:

        staff_from = request.form.get("staff_from") or None
        store_close = request.form.get("store_close") or None

        schedule_service.update_day_hours(
            schedule_id,
            edit_day,
            staff_from,
            store_close
        )

        # redirect tylko po POST
        return redirect(url_for(
            "schedule_bp.schedule_details",
            schedule_id=schedule_id,
            edit_day=edit_day
        ))

    # =====================================
    # POBRANIE DANYCH DO WIDOKU
    # =====================================
    schedule = schedule_service.get_schedule(schedule_id)
    matrix = schedule_service.get_month_matrix(schedule_id)

    # =====================================
    # SZUKANIE DANYCH DNIA
    # =====================================
    day_data = None

    if edit_day:
        for d in matrix["days"]:
            if d["day"] == edit_day:
                day_data = d
                break

    # =====================================
    # RENDER
    # =====================================
    return render_template(
        "schedule_month.html",
        schedule=schedule,
        matrix=matrix,
        edit_day=edit_day,
        day_data=day_data
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

#=======================================================
# Edycja dnia WebUI
# url: /schedules/update_day
#=======================================================

@schedule_bp.route("/day/<int:day_id>", methods=["GET", "POST"])
@login_required
def edit_schedule_day(day_id):

    # pobierz dane dnia (dopasuj metodę do swojego service)
    day = schedule_service.get_schedule_day(day_id)

    if request.method == "POST":
        staff_from = request.form["staff_from"]
        store_close = request.form["store_close"]

        schedule_service.update_schedule_day_hours(
            day_id,
            staff_from,
            store_close
        )

        return redirect(
            url_for(
                "schedule_bp.schedule_details",
                schedule_id=day["schedule_id"]
            )
        )

    return render_template("schedule_day_edit.html", day=day)


@schedule_bp.route("/<int:schedule_id>/day/<int:day>")
@login_required
def schedule_day(schedule_id, day):
    schedule = schedule_service.get_schedule(schedule_id)
    matrix = schedule_service.get_month_matrix(schedule_id)

    return render_template(
        "schedule_day.html",
        schedule=schedule,
        matrix=matrix,
        day=day
    )
