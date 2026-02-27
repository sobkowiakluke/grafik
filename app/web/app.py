
from flask import Flask, redirect, url_for
from flask_login import login_required

from app.web.extensions import login_manager
from app.db.provider import close_db

from app.web.routes_employee import employee_bp
from app.web.routes_schedule import schedule_bp
from app.web.auth import auth_bp   # ← TERAZ blueprint!


app = Flask(__name__)
app.secret_key = "change_me"


# DB lifecycle
app.teardown_appcontext(close_db)


# Login manager
login_manager.init_app(app)
login_manager.login_view = "auth.login"


# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp, url_prefix="/employees")
app.register_blueprint(schedule_bp, url_prefix="/schedules")


# Root

from flask import render_template

@app.route("/")
@login_required
def index():
    return render_template("main.html")
