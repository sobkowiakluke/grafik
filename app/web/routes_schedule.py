from flask import Blueprint, render_template
from flask_login import login_required
from app.services.schedule_service import ScheduleService

from app.db.connection import Database
from app.services.schedule_day_service import ScheduleDayService

schedule_bp = Blueprint('schedule_bp', __name__, template_folder='templates')

db = Database()
day_service = ScheduleDayService(db)
schedule_service = ScheduleService(db, day_service)


@schedule_bp.route("/list")
@login_required
def list_schedules():
    schedules = schedule_service.list_schedules()
    return render_template("schedule_list.html", schedules=schedules)

@schedule_bp.route("/<int:schedule_id>")
@login_required
def view_schedule(schedule_id):
    schedule = schedule_service.get_schedule(schedule_id)
    days = day_service.list_days(schedule_id)
    return render_template(
        "schedule_view.html",
        schedule=schedule,
        days=days
    )
