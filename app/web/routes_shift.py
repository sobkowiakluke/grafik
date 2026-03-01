from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

shift_bp = Blueprint("shift", __name__, url_prefix="/shifts")


@shift_bp.route("/new", methods=["GET"])
@login_required
def new_shift():
    return render_template("shift_form.html")

@shift_bp.route("/new", methods=["GET"])
def create_shift_form():
    return render_template("shift/shift_form.html")

@shift_bp.route("", methods=["POST"])
@login_required
def create_shift():
    # tu później shift_service.create_shift(...)
    return "<p>Zmiana zapisana (na razie symulacja)</p>"
