from flask import Blueprint, render_template
from flask_login import login_required
from app.services.schedule_service import ScheduleService

from app.db.connection import Database
from app.services.schedule_day_service import ScheduleDayService
from app.services.schedule_service import ScheduleService

schedule_bp = Blueprint('schedule_bp', __name__, template_folder='templates')

db = Database()
day_service = ScheduleDayService(db)
schedule_service = ScheduleService(db, day_service)


@schedule_bp.route("/list")
@login_required
def list_schedules():
    schedules = schedule_service.list_schedules()
    return render_template("schedule_list.html", schedules=schedules)
