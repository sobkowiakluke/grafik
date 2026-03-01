from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, UserMixin

from app.web.extensions import login_manager
from app.db.provider import get_db
from werkzeug.security import check_password_hash

# =====================================================
# Blueprint
# =====================================================
auth_bp = Blueprint("auth", __name__)


# =====================================================
# USER MODEL
# =====================================================
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


# =====================================================
# USER LOADER
# =====================================================
@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id, username FROM users WHERE id=%s",
        (user_id,),
    )

    row = cur.fetchone()
    cur.close()

    if not row:
        return None

    return User(row["id"], row["username"])


# =====================================================
# LOGIN
# =====================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        cur = db.cursor()

        cur.execute(
            "SELECT id, username, password FROM users WHERE username=%s",
            (username,),
        )

        user = cur.fetchone()
        cur.close()

        if not user:
            flash("Nieprawidłowy login lub hasło", "danger")
            return redirect(url_for("auth.login"))

        from werkzeug.security import check_password_hash

        if not check_password_hash(user["password"], password):
            flash("Nieprawidłowy login lub hasło", "danger")
            return redirect(url_for("auth.login"))

        login_user(User(user["id"], user["username"]))
        return redirect(url_for("index"))

    # KLUCZOWE — musi być poza IF
    return render_template("login.html")

# =====================================================
# LOGOUT
# =====================================================
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
