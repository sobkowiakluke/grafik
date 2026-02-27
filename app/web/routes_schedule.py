from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from app.db.provider import get_db
from app.services.schedule_service import ScheduleService
from app.services.schedule_day_service import ScheduleDayService


# =====================================================
# Blueprint
# =====================================================
schedule_bp = Blueprint("schedule_bp", __name__)


# =====================================================
# Service factory (bez globalnego Database)
# =====================================================
def get_schedule_service():
    db = get_db()
    day_service = ScheduleDayService(db)
    return ScheduleService(db, day_service)


# =====================================================
# Lista grafików
# URL: /schedules/list
# =====================================================
@schedule_bp.route("/list")
@login_required
def list_schedules():

    service = get_schedule_service()

    sort = request.args.get("sort", "year")
    order = request.args.get("order", "desc")

    schedules = service.list_schedules(sort=sort, order=order)

    return render_template(
        "schedule_list.html",
        schedules=schedules,
        current_sort=sort,
        current_order=order,
    )

# =====================================================
# Szczegóły grafiku
# URL: /schedules/<id>
# =====================================================
@schedule_bp.route("/<int:schedule_id>", methods=["GET", "POST"])
@login_required
def schedule_details(schedule_id):

    service = get_schedule_service()

    edit_day = request.args.get("edit_day", type=int)

    # =====================================
    # ZAPIS GODZIN (POST)
    # =====================================
    if request.method == "POST" and edit_day:

        staff_from = request.form.get("staff_from") or None
        store_close = request.form.get("store_close") or None

        service.update_day_hours(
            schedule_id,
            edit_day,
            staff_from,
            store_close
        )

        return redirect(url_for(
            "schedule_bp.schedule_details",
            schedule_id=schedule_id,
            edit_day=edit_day
        ))

    # =====================================
    # POBRANIE DANYCH
    # =====================================
    schedule = service.get_schedule(schedule_id)
    matrix = service.get_month_matrix(schedule_id)

    day_data = None
    if edit_day:
        for d in matrix["days"]:
            if d["day"] == edit_day:
                day_data = d
                break

    return render_template(
        "schedule_month.html",
        schedule=schedule,
        matrix=matrix,
        edit_day=edit_day,
        day_data=day_data
    )


# =====================================================
# Widok miesiąca
# URL: /schedules/<id>/month
# =====================================================
@schedule_bp.route("/<int:schedule_id>/month")
@login_required
def schedule_month(schedule_id):
    service = get_schedule_service()
    schedule, matrix = service.get_schedule_month_matrix(schedule_id)

    return render_template(
        "schedule_month.html",
        schedule=schedule,
        matrix=matrix
    )


# =====================================================
# Dodawanie grafiku
# URL: /schedules/add
# =====================================================
@schedule_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_schedule():

    service = get_schedule_service()

    if request.method == "POST":
        year = int(request.form["year"])
        month = int(request.form["month"])

        service.create_schedule(year, month)

        return redirect(url_for("schedule_bp.list_schedules"))

    return render_template("schedule_add.html")


# =====================================================
# Edycja dnia
# URL: /schedules/day/<id>
# =====================================================
@schedule_bp.route("/day/<int:day_id>", methods=["GET", "POST"])
@login_required
def edit_schedule_day(day_id):

    service = get_schedule_service()
    day = service.get_schedule_day(day_id)

    if request.method == "POST":
        staff_from = request.form["staff_from"]
        store_close = request.form["store_close"]

        service.update_schedule_day_hours(
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


# =====================================================
# Widok pojedynczego dnia
# URL: /schedules/<id>/day/<day>
# =====================================================
@schedule_bp.route("/<int:schedule_id>/day/<int:day>")
@login_required
def schedule_day(schedule_id, day):

    service = get_schedule_service()

    schedule = service.get_schedule(schedule_id)
    matrix = service.get_month_matrix(schedule_id)

    return render_template(
        "schedule_day.html",
        schedule=schedule,
        matrix=matrix,
        day=day
    )
